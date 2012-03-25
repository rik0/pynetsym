import abc
import collections
import functools
import numbers
import gevent

import gevent.queue as queue

_M = collections.namedtuple('Message', 'sender payload')

class Message(_M):
    """
    An immutable object that is used to send a message among agents.
    """


class AddressingError(Exception):
    """
    Error signaling that something with the addressing of a message went wrong.

    """

    def __init__(self, *args, **kwargs):
        super(AddressingError, self).__init__(*args, **kwargs)


class AddressBook(object):
    """
    The Address book holds information on every agent in the system.

    An agent that is not in the AddressBook is virtually unreachable.

    @todo: Change the API so that the identifier is not chosen from outside.
        The API change should take into account:
            1. how it works with different Graph implementations (e.g., igraph)
            2. how it works with different back-ends (e.g., asside)
    """

    RAND_CHARS = 6 #: ivar: Number of random characters appended to duplicate string id

    def __init__(self, graph):
        self.name_registry = {}
        self.graph = graph

    def register(self, identifier, agent):
        """
        Binds the identifier with the agent

        @param identifier: the identifier to bind the agent to
        @type identifier: int | str
        @param agent: the agent to bind
        @type agent: Agent
        @raise AddressingError: if identifier is already bound and is numeric.
        @raise TypeError: if the identifier is not a string or a integer
        """
        if isinstance(identifier, basestring):
            if (identifier in self.name_registry
                    and self.name_registry[identifier] is not agent):
                raise AddressingError(
                    "Could not rebing agent %r to identifier %r." % (agent, identifier))
            else:
                self.name_registry[identifier] = agent
        elif isinstance(identifier, numbers.Integral):
            if identifier in self.graph:
                raise AddressingError(
                    "Could not rebing agent %r to identifier %r." % (agent, identifier))
            else:
                self.graph.add_node(identifier, agent)
        else:
            raise TypeError("Identifiers must be strings or integers")

    def resolve(self, identifier):
        """
        Resolves :param: identifier to the actual agent.

        @raise AddressingError: if the agent is not registered.
        """
        if isinstance(identifier, basestring):
            try:
                return self.name_registry[identifier]
            except KeyError:
                raise AddressingError(
                    "Could not find node with address %r." % identifier)
        elif isinstance(identifier, numbers.Integral):
            try:
                return self.graph[identifier]
            except RuntimeError as e:
                raise AddressingError(e.message)



class AbstractAgent(object):
    """
    An Agent is the basic class of the simulation. Agents communicate
    asynchronously with themselves.
    """

    __metaclass__ = abc.ABCMeta

    IGNORE = 0
    LOG_ERROR = 1
    EXCEPTION = 2

    def __init__(self, identifier, address_book, error_level=LOG_ERROR):
        """
        Initializes the Agent object setting variables and registering
        the agent in the address book.

        @param identifier: the identifier the agent has in the system
        @type identifier: int|str
        @param address_book: the address book where we want to register
        @type address_book: AddressBook
        @param error_level: describe what should happen when a message
            cannot be delivered
        @type error_level: int (IGNORE|LOG_ERROR|EXCEPTION)
        @return: the Agent
        """
        self._id = identifier
        self._address_book = address_book
        self._address_book.register(identifier, self)
        self._err_level = error_level

    @abc.abstractmethod
    def deliver(self, message):
        """
        Delivers message to this agent.
        @param message: the message
        @type message: Message
        """
        pass

    @abc.abstractmethod
    def read(self):
        """
        Reads the next message that was sent to this agent.
        @attention: It is not really meant to be called directly.
        @return: Message
        """
        pass

    @abc.abstractmethod
    def cooperate(self):
        """
        Release control

        """
        pass

    @property
    def id(self):
        """
        The node identifier.
        @rtype: int
        @attention: In fact, the only requirement is that it is hashable
        """
        return self._id

    def send(self, receiver_id, payload, **additional_parameters):
        """
        Send a message to the specified agent.

        @param receiver_id: the id of the receiving agent
        @param payload: the name of the receiving agent method or a function
            taking the agent as its first argument (unbound methods are just
            perfect).
        @param additional_parameters: additional parameters to be passed to
            the function
        """
        receiver = self._address_book.resolve(receiver_id)
        if callable(payload):
            func = functools.partial(payload, **additional_parameters)
        else:
            receiver_class = type(receiver)
            try:
                unbound_method = getattr(receiver_class, payload)
            except AttributeError:
                additional_parameters = dict(
                    name=payload,
                    additional_parameters=additional_parameters)
                unbound_method = getattr(
                    receiver_class,
                    'unsupported_message')
            func = functools.partial(unbound_method, **additional_parameters)
        receiver.deliver(Message(self.id, func))

    def process(self, message):
        """
        Processes the message. This means calling the message payload with
        self as argument.

        """
        return message.payload(self)

    def run_loop(self):
        """
        Agent main run loop.

            1. read a message from the queue
            2. process the message and elaborate the answer
            3. if the answer is not None, send it to the original message
            4. release control

        @attention: checks regarding message_processor and similar are not made
        """
        while 1:
            message = self.read()
            answer = self.process(message)
            if answer is not None:
                try:
                    answer, answer_parameters = answer
                except TypeError:
                    answer_parameters = {}
                self.send(message.sender, answer, **answer_parameters)
            self.cooperate()

    def unsupported_message(self, name, additional_parameters):
        """
        Prints out something if we received a message we could not process.
        """
        print (
            '%s received "%s" message with parameters %s: could not process.' %
            (self, name, additional_parameters))

    def __str__(self):
        return '%s(%s)' % (type(self), self.id)

class AgentIdUpdatableContext(object):
    """
    Agent ids are normally not settable because doing so could prevent
    the system from functioning correctly. However, in certain circumstances
    it makes sense to change a node identifier instead of destroying the old
    node and creating a new one.

    In this context agent ids become settable. Notice that the changes
    are *not* automatically reflected in the address book.
    """
    def __enter__(self):
        def id_setter(self, new_id):
            self._id = new_id

        self.old_property = AbstractAgent.id
        AbstractAgent.id = property(
            fget=self.old_property,
            fset=id_setter)

    def __exit__(self, *args):
        AbstractAgent.id = self.old_property



class Agent(gevent.Greenlet, AbstractAgent):
    def __init__(self, identifier, address_book,
            error_level=AbstractAgent.LOG_ERROR,
            *args, **kwargs):
        super(Agent, self).__init__(*args, **kwargs)
        AbstractAgent.__init__(self, identifier, address_book, error_level)
        self._queue = queue.Queue()

    def deliver(self, message):
        self._queue.put(message)

    def read(self):
        """
        Reads the next message that was sent to this agent.
        @attention: It is not really meant to be called directly.
        @return: Message
        """
        return self._queue.get()

    def cooperate(self):
        """
        Release control

        """
        gevent.sleep()

    def _run(self):
        self.run_loop()


class Node(Agent):
    """
    A Node in the social network.
    """

    def __init__(self, identifier, address_book, graph):
        """
        Create a Node in the network.
        @param identifier: the identifier to bind the Node to
        @type identifier: int|str
        @param address_book: the address book where we want to register
        @type address_book: AddressBook
        @param graph: the graph backing the social network
        @type graph: networkx.Graph
        @return: the Node
        """
        super(Node, self).__init__(identifier, address_book)
        self.graph = graph

    def link_to(self, criterion_or_node):
        """
        Sends an 'accept_link' message to the specified node.

        @param criterion_or_node: The node to link may be an identifier
            or a callable extracting the node from the graph
        @type criterion_or_node: id | callable(L{graph<graph.Graph>}) -> L{Node<Node>}
        @return: None
        """
        if callable(criterion_or_node):
            target_node = criterion_or_node(self.graph)
        else:
            target_node = criterion_or_node
        self.send(target_node, 'accept_link', originating_node=self.id)

    def accept_link(self, originating_node):
        """
        Accepts an 'accept_link' message (modifying the network).

        @param originating_node: the node that required the connection
        @type originating_node: id
        """
        self.graph.add_edge(originating_node, self.id)
