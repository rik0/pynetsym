import abc
import collections
import functools
import numbers
import gevent
import itertools as it

import gevent.queue as queue
import sys

from pynetsym import rnd

def answers(method):
    """
    Marks a message to which we expect response. Accordingly to options
    a method answering to such message that does not return anything raises
    exceptions or logs an error or is ignored.
    @param method: the method to decorate
    @return: the decorated method
    """
    method.answers = True
    return method


def message_processor(method):
    """
    Marks a method that actually processes a message
    @param method: the method to decorate
    @return: the decorated method
    """
    method.message_processor = True
    return method


def is_message_processor(method):
    """
    Returns True if method is a message processor
    @param method: the method to check
    @return: True if method is a message processor
    """
    return (hasattr(method, 'message_processor')
            and method.message_processor)


def does_answer(method):
    """
    Returns True if method should answer.
    @param method: the method to check
    @return: True if method should answer
    """
    return (hasattr(method, 'answers')
            and method.answers)

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

    def __init__(self):
        self.registry = {}

    def _check_same_agent_or_fail(self, agent, identifier):
        old_agent = self.registry[identifier]
        if old_agent is agent:
            pass
        else:
            message = ("Rebinding agent %s from %s to %s" %
                       (identifier, old_agent, agent))
            raise AddressingError(message)

    def register(self, identifier, agent):
        """
        Binds the identifier with the agent

        @param identifier: the identifier to bind the agent to
        @param agent: the agent to bind
        @raise AddressingError: if identifier is already bound.
        """
        if identifier in self.registry:
            self._check_same_agent_or_fail(agent, identifier)
        else:
            self.registry[identifier] = agent

    def unregister(self, id_or_agent):
        """
        Unbinds the specified agent.

        @param id_or_agent: the id or the agent to bind
        @type id_or_agent: id | Agent
        @raise AddressingError: if id was not bound.

        """
        try:
            self.registry.pop(id_or_agent)
        except KeyError:
            try:
                self.registry.pop(id_or_agent.id)
            except (AttributeError, KeyError) as e:
                raise AddressingError(e)

    def rebind(self, id, new_agent):
        """
        Removes any existing binding of id and binds id with the new agent.

        @raise AddressingError: if id was not bound.

        """
        self.unregister(id)
        self.register(id, new_agent)

    def force_rebind(self, id, new_agent):
        """
        Like rebind, but always succeeds.

        """
        try:
            self.rebind(id, new_agent)
        except AddressingError:
            self.register(id, new_agent)

    def resolve(self, identifier):
        """
        Resolves :param: identifier to the actual agent.

        @raise AddressingError: if the agent is not registered.
        """
        try:
            return self.registry[identifier]
        except KeyError, e:
            raise AddressingError(e)

    def agents(self):
        """
        Return the sequence of agent addresses.

        """
        return self.registry.keys()

    def create_id_from_hint(self, hint):
        """
        Creates a valid identifier starting from hint.
        If hint was not bound to an agent, it is hint. Otherwise, if
        hint is a string, builds a string appending random characters to
        hint. If hint was an integer, it returns a random number among
        the free identifiers between the minimum and the maximum registered
        numbers. If such set is empty, return the lowest free integer number.

        @param hint: the starting identifier
        @type hint: int|str
        @return: an identifier no agent is registered to.
        @raise TypeError: if hint is not string or int
        """
        if (hint not in self.registry
            and isinstance(hint, (numbers.Integral, basestring))):
            return hint
        elif isinstance(hint, numbers.Integral):
            numeric_keys = sorted(k for k in self.registry.iterkeys()
            if isinstance(k, numbers.Integral))
            min_key = numeric_keys[0]
            max_key = numeric_keys[-1]
            free_keys = (set(xrange(min_key, max_key + 1))
                         - set(numeric_keys))
            if free_keys:
                return free_keys.pop()
            else:
                ## keys from min_key to max_key are taken
                ## try a smaller key, otherwise, try greater
                ## we want to keep the keys as bounded as possible
                if min_key - 1 >= 0:
                    return min_key - 1
                else:
                    return max_key + 1
        elif isinstance(hint, basestring):
            return ''.join(
                it.chain(hint, '#',
                         it.islice(rnd.random_printable_chars(),
                                   0, self.RAND_CHARS)))
        else:
            raise TypeError(
                "Could not build identifier from {}".format(hint))


class AbstractAgent(object):
    """
    An Agent is the basic class of the simulation. Agents communicate
    asynchronously with themselves.
    """

    __metaclass__ = abc.ABCMeta

    IGNORE = 0
    LOG_ERROR = 1
    EXCEPTION = 2

    def initialize(self, identifier, address_book, error_level=LOG_ERROR):
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
        @rtype: string | int
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
                except ValueError:
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

class Agent(gevent.Greenlet, AbstractAgent):
    def __init__(self, identifier, address_book,
                 error_level=AbstractAgent.LOG_ERROR,
                 *args, **kwargs):
        super(Agent, self).__init__(*args, **kwargs)
        self.initialize(identifier, address_book, error_level)
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

class NodeManager(Agent):
    """
    The class responsible to create nodes.

    """

    name = 'manager' #: @ivar: the registered name in the L{address book<AddressBook>}

    def __init__(self, graph, address_book, configurator):
        super(NodeManager, self).__init__(NodeManager.name, address_book)
        self.graph = graph
        self.configurator = configurator

    def _run(self):
        if callable(self.configurator):
            self.configurator(self)
        else:
            self.configurator.setup(self)
        self.run_loop()

    def create_node(self, cls, identifier_hint, parameters):
        """
        Creates a new node.

        @param cls: the factory creating the new node. Usually the node class.
        @type cls: callable
        @param identifier_hint: the identifier to bind the new node to
        @type identifier_hint: L{identifier<Node.id>}
        @param parameters: the parameters that are forwarded to the node for
            creation
        @type parameters: dict
        @return: the actual identifier
        @rtype: int | str
        """

        identifier = self._address_book.create_id_from_hint(identifier_hint)
        node = cls(identifier, self._address_book,
                   self.graph, **parameters)
        node.link_value(self.node_terminated_hook)
        node.link_exception(self.node_failed_hook)
        node.start()
        return 'created_node', dict(identifier=identifier)

    def node_failed_hook(self, node):
        """
        Hooks an exception in the node. This implementation only prints stuff.

        @param node: the node that failed.
        @type node: Node
        """
        print >> sys.stderr, "Node failed: {}\n{}".format(node, node.exception)

    def node_terminated_hook(self, node):
        """
        Hooks a node termination. Usually nothing has to be done.

        @param node: the node that terminated.
        @type node: Node

        """
        pass


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
        self.graph.add_node(self.id)

    def link_to(self, criterion_or_node):
        """
        Sends an 'accept_link' message to the specified node.

        @param criterion_or_node: The node to link may be an identifier
            or a callable extracting the node from the graph
        @type criterion_or_node: id | callable(L{graph<graph.Graph>}) -> L{Node<Node>}
        @return:
        """
        if callable(criterion_or_node):
            target_node = criterion_or_node(self.graph)
        else:
            target_node = criterion_or_node
        self.send(target_node, Node.accept_link, originating_node=self.id)

    def accept_link(self, originating_node):
        """
        Accepts an 'accept_link' message (modifying the network).

        @param originating_node: the node that required the connection
        @type originating_node: id
        """
        self.graph.add_edge(originating_node, self.id)