import collections
import itertools as it
import gevent
import gevent.queue as queue
import pa_utils

def uniform_spawn_strategy(klass):
    def uniform_spawn_strategy_aux(
            identifiers, address_book,
            graph, parameters):
        return it.izip(
            it.repeat(klass),
            identifiers,
            it.repeat(address_book),
            it.repeat(graph),
            it.repeat(parameters))

    return uniform_spawn_strategy_aux


Message = collections.namedtuple('Message', 'sender payload')

class Agent(gevent.Greenlet):
    def __init__(self, identifier, address_book, *args, **kwargs):
        super(Agent, self).__init__(*args, **kwargs)
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
        sender = self._address_book.resolve(receiver_id)
        sender.deliver(Message(self.id, payload))

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
        self.run_loop()

    def create_node(self, cls, identifier, parameters):
        node = cls(identifier, self._address_book, self.graph, **parameters)
        node.link(self.node_terminated_hook)
        node.start()

    def node_terminated_hook(self, node):
        print node
        pass

class Node(Agent):
    def __init__(self, identifier, address_book,
                 graph, *args, **kwargs):
        super(Node, self).__init__(
            identifier, address_book,
            *args, **kwargs)
        self.graph = graph
        self.graph.add_node(self.id)


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