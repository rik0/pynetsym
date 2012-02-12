import collections
import functools
import gevent

import gevent.queue as queue

from abc import abstractmethod, ABCMeta

Message = collections.namedtuple('Message', 'sender payload')

class AddressingError(Exception):
    def __init__(self, *args, **kwargs):
        super(AddressingError, self).__init__(*args, **kwargs)

# TODO: we should streamline the API to avoid which occur in registering an agent
#       with an identifier different from its "address"
class AddressBook(object):
    """
    The Address book holds information on every agent in the system.

    An agent that is not in the AddressBook is virtually unreachable.

    """
    def __init__(self):
        self.registry = {}

    def _check_same_agent(self, agent, identifier):
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
            self._check_same_agent(agent, identifier)
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
            except (AttributeError, KeyError), e:
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

class Agent(gevent.Greenlet):
    """
    An Agent is the basic class of the simulation. Agents communicate
    asynchronously with themselves.
    """
    def __init__(self, identifier, address_book):
        super(Agent, self).__init__()
        self._queue = queue.Queue()
        self._id = identifier
        self._address_book = address_book
        self._address_book.register(identifier, self)

    @property
    def id(self):
        """
        The node identifier.
        @rtype: string | int
        @attention: In fact, the only requirement is that it is hashable
        """
        return self._id

    def _deliver(self, message):
        self._queue.put(message)

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
                    name=payload, additional_parameters=additional_parameters
                )
                unbound_method = getattr(receiver_class, 'unsupported_message')
            func = functools.partial(unbound_method, **additional_parameters)
        receiver._deliver(Message(self.id, func))


    def read(self):
        return self._queue.get()

    def process(self, message):
        return message.payload(self)

    def cooperate(self):
        gevent.sleep()

    def run_loop(self):
        while 1:
            message = self.read()
            answer = self.process(message)
            if answer is not None:
                self.send(message.sender, answer)
            self.cooperate()

    def unsupported_message(self, name, additional_parameters):
        print ('%s received "%s" message with parameters %s: could not process.' %
                    (self, name, additional_parameters))

    def _run(self):
        self.run_loop()

    def __str__(self):
        return '%s(%s)' % (type(self), self.id)


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

    def create_node(self, cls, identifier, parameters):
        """
        Creates a new node.

        @param cls: the factory creating the new node. Usually the node class.
        @type cls: callable
        @param identifier: the identifier to bind the new node to
        @type identifier: L{identifier<Node.id>}
        @param parameters: the parameters that are forwarded to the node for
            creation
        @type parameters: dict
        """
        node = cls(identifier, self._address_book, self.graph, **parameters)
        node.link_value(self.node_terminated_hook)
        node.link_exception(self.node_failed_hook)
        node.start()

    def node_failed_hook(self, node):
        """
        Hooks an exception in the node. This implementation only prints stuff.

        @param node: the node that failed.
        @type node: Node
        """
        print >> std.error, "Node failed: {}\n{}".format(node, node.exception)

    def node_terminated_hook(self, node):
        pass

class Node(Agent):
    """
    A Node in the social network.
    """
    def __init__(self, identifier, address_book, graph):
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