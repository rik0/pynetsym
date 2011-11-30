import collections
import logging
import gevent
import pa_utils

import gevent.queue as queue

from abc import abstractmethod, ABCMeta

Message = collections.namedtuple('Message', 'sender payload')

class AddressingError(Exception):
    def __init__(self, *args, **kwargs):
        super(AddressingError, self).__init__(*args, **kwargs)

class AddressBook(object):
    def __init__(self):
        self.registry = {}

    def register(self, identifier, agent, check=None):
        if check is None:
            self._log_if_rebind(identifier, agent)
            self.registry[identifier] = agent
        elif check(identifier, agent):
            self.registry[identifier] = agent


    def unregister(self, id_or_agent):
        try:
            self.registry.pop(id_or_agent)
        except KeyError:
            for k, v in self.registry.iteritems():
                if v is id_or_agent:
                    break
            else:
                return
            self.registry.pop(k)

    def resolve(self, identifier):
        try:
            return self.registry[identifier]
        except KeyError, e:
            raise AddressingError(e)

    def _log_if_rebind(self, identifier, agent):
        try:
            old_agent = self.registry[identifier]
            if old_agent is agent:
                pass
            else:
                logging.warning(
                    "Rebinding agent %s from %s to %s",
                    identifier, old_agent, agent)
        except KeyError:
            # ok
            pass
        return True

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

    def send(self, receiver_id, payload):
        receiver = self._address_book.resolve(receiver_id)
        if callable(payload):
            receiver.deliver(Message(self.id, payload))
        else:
            unbound_method = getattr(type(receiver), payload)
            receiver.deliver(Message(self.id, unbound_method))


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

    def _run(self):
        self.run_loop()

    def __str__(self):
        return '%s(%s)' % (type(self), self.id)


class NodeManager(Agent):
    name = 'manager'

    def __init__(self, graph, address_book, generation_feed):
        super(NodeManager, self).__init__(NodeManager.name, address_book)
        self.graph = graph
        self.generation_feed = generation_feed

    def _run(self):
        self.generation_feed(self)
        #self.run_loop()

    def create_node(self, cls, identifier, parameters):
        node = cls(identifier, self._address_book, self.graph, **parameters)
        node.link(self.node_terminated_hook)
        node.start()

    def node_terminated_hook(self, node):
        print node
        pass


class Node(Agent):
    __metaclass__ = ABCMeta

    def __init__(self, identifier, address_book, graph):
        super(Node, self).__init__(identifier, address_book)
        self.graph = graph
        self.graph.add_node(self.id)

    @abstractmethod
    def activate(self):
        pass


def introduce_self_to_popular(node, sample_size=1):
    graph = node.graph
    nodes = pa_utils.preferential_attachment(graph, sample_size)
    for target_node in nodes:
        node.send(target_node, make_accept_link(node.id))


def make_accept_link(originating_node):
    def accept_link(node):
        graph = node.graph
        graph.add_edge(originating_node, node.id)

    return accept_link
