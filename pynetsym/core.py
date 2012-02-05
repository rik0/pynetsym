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
        if identifier in self.registry:
            self._check_same_agent(agent, identifier)
        else:
            self.registry[identifier] = agent

    def unregister(self, id_or_agent):
        try:
            self.registry.pop(id_or_agent)
        except KeyError:
            try:
                self.registry.pop(id_or_agent.id)
            except (AttributeError, KeyError), e:
                raise AddressingError(e)

    def rebind(self, id, new_agent):
        self.unregister(id)
        self.register(id, new_agent)

    def resolve(self, identifier):
        try:
            return self.registry[identifier]
        except KeyError, e:
            raise AddressingError(e)

class Agent(gevent.Greenlet):
    def __init__(self, identifier, address_book):
        super(Agent, self).__init__()
        self._queue = queue.Queue()
        self._id = identifier
        self._address_book = address_book
        self._address_book.register(identifier, self)

    @property
    def id(self):
        return self._id

    def deliver(self, message):
        self._queue.put(message)

    def send(self, receiver_id, payload, **additional_parameters):
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
        receiver.deliver(Message(self.id, func))

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
    name = 'manager'

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
        node = cls(identifier, self._address_book, self.graph, **parameters)
        node.link_value(self.node_terminated_hook)
        node.link_exception(self.node_failed_hook)
        node.start()

    def node_failed_hook(self, node):
        print node.exception

    def node_terminated_hook(self, node):
        pass

class Node(Agent):
    def __init__(self, identifier, address_book, graph):
        super(Node, self).__init__(identifier, address_book)
        self.graph = graph
        self.graph.add_node(self.id)

    def link_to(self, criterion_or_node):
        if callable(criterion_or_node):
            target_node = criterion_or_node(self.graph)
        else:
            target_node = criterion_or_node
        self.send(target_node, Node.accept_link, originating_node=self.id)
        
    def accept_link(self, originating_node):
        self.graph.add_edge(originating_node, self.id)