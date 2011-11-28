from Carbon.Dialogs import ok
import abc
import logging
import random
import gevent
import collections
from gevent.greenlet import Greenlet

import networkx as nx
import itertools as it

from gevent import queue


def uniform_spawn_strategy(klass):
    def uniform_spawn_strategy_aux(
            identifiers, address_book,
            network_spy, parameters):
        return it.izip(
            it.repeat(klass),
            identifiers,
            it.repeat(address_book),
            it.repeat(network_spy),
            it.repeat(parameters))
    return uniform_spawn_strategy_aux

class NodeManager(gevent.Greenlet):
    name = 'manager'
    def __init__(self, spawn_strategy,
                 network_spy, address_book,
                 network_size, **kwargs):
        self.spawn_strategy = spawn_strategy
        self.network_spy = network_spy
        self.address_book = address_book
        self.network_size = network_size
        self.params = kwargs
        self.simulation_terminated = False
        super(NodeManager, self).__init__()

    def _run(self):
        for klass, identifier, address_book, network_spy, parameters \
            in self.build_greenlet_parameters():
            node = klass(identifier, address_book,
                         network_spy, **parameters)
            node.link(self.node_terminated_hook)
            node.start()
        ## something here should say "process exceptions when they occur
        ## maybe make it an agent!

    def node_terminated_hook(self, node):
        pass

    def build_greenlet_parameters(self):
        return self.spawn_strategy(
                xrange(self.network_size),
                self.address_book, self.network_spy,
                self.params)

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
        if isinstance(id_or_agent, Agent):
            self._unregister_by_value(id_or_agent)
        else:
            self.registry.pop(id_or_agent)

    def _unregister_by_value(self, agent):
        for k, v in self.registry.iteritems():
            if v is agent:
                break
        else:
            return
        self.registry.pop(k)

    def resolve(self, identifier):
        try:
            return self.registry[identifier]
        except KeyError:
            raise AddressingError

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


Message = collections.namedtuple('Message', 'sender payload')

class Agent(gevent.Greenlet):
    def __init__(self, identifier, address_book, *args, **kwargs):
        super(Agent, self).__init__(run=None, *args, **kwargs)
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

    def run_loop(self):
        while 1:
            message = self.read()
            answer = self.process(message)
            if answer is not None:
                self.send(message.sender, answer)

    def _run(self):
        self.run_loop()

    def __str__(self):
        return '%s(%s)' % (type(self), self.id)

class Activator(Agent):
    name = 'activator'
    def __init__(self, activate_function, network_spy, address_book):
        super(Activator, self).__init__(self.name, address_book)
        self.network_spy = network_spy
        self.activate_function = activate_function

    def tick(self):
        node_id = self.choose_node()
        self.send(node_id, self.activate_function)

    def simulation_ended(self):
        for node_id in self.network_spy.nodes():
            self.send(node_id, Greenlet.kill)
        self.kill()

    def choose_node(self):
        return random.choice(self.network_spy.nodes())


class Clock(Agent):
    name = 'clock'
    def __init__(self, max_steps, address_book):
        super(Clock, self).__init__(self.name, address_book)
        self.max_steps = max_steps
        self.activator = address_book.resolve(Activator.name)

    def _run(self):
        activator_tick = type(self.activator).tick
        activator_end = type(self.activator).simulation_ended
        for step in xrange(self.max_steps):
            self.send(Activator.name, activator_tick)
        self.send(Activator.name, activator_end)

def make_activator(max_steps, activate_function, network_spy, address_book):
    activator = Activator(activate_function, network_spy, address_book)
    clock = Clock(max_steps, address_book)
    activator.start()
    gevent.sleep(0)
    clock.start()
    return activator


class Node(Agent):
    def __init__(self, identifier, address_book,
                 network_spy, *args, **kwargs):
        super(Node, self).__init__(identifier, address_book, *args, **kwargs)
        self.network_spy = network_spy
        self.network_spy.add_node(self.id)

class TLNode(Node):
    def __init__(self, identifier, address_book,
                 network_spy, *args, **kwargs):
        self.p = kwargs.pop('death_probability')
        super(TLNode, self).__init__(identifier, address_book, network_spy, *args, **kwargs)

def FAIL(_node):
    pass

def tl_accept_link(originating_node):
    def tl_accept_link_aux(node):
        graph = node.network_spy
        graph.add_edge(originating_node, node.id)
    return tl_accept_link_aux

def tl_introduce(target_node):
    def introduce_aux(node):
        graph = node.network_spy
        if graph.has_edge(node.id, target_node):
            return tl_introduction_failed
        else:
            node.send(target_node, tl_accept_link(node.id))
    return introduce_aux

def tl_introduction_failed(node):
    introduce_self_to_popular(node)


def preferential_attachment(graph, sample_size=1):
    # try to use edges to make sampling easier!
    number_of_edges = graph.no_edges()
    population = graph.nodes()

    while 1:
        candidate = random.choice(population)
        acceptance_probability = nx.degree(graph, candidate)
        if (random.randint(0, number_of_edges) < acceptance_probability
            and sample_size > 0):
            yield candidate
            sample_size -= 1

def introduce_self_to_popular(node, sample_size=1):
    graph=node.network_spy
    nodes = preferential_attachment(graph, sample_size)
    for target_node in nodes:
        node.send(target_node, tl_accept_link)


def tl_activate(node):
    graph = node.network_spy
    neighbors = nx.neighbors(graph, node.id)

    if len(neighbors) > 1:
        node_a, node_b = random.sample(neighbors, 2)
        node.send(node_a, tl_introduce(node_b))
        # if we have two friends that are connected, find new ones

    introduce_self_to_popular(node)


def main(steps, activate_function, spawn_strategy, nodes_number, p):
    network_spy = nx.Graph()
    address_book = AddressBook()
    node_manager = NodeManager(spawn_strategy, network_spy,
                                address_book,
                                network_size=nodes_number,
                                death_probability=p)
    node_manager.start()
    activator = make_activator(steps, activate_function, network_spy, address_book)
    activator.join()
    node_manager.join()
    return network_spy


if __name__ == '__main__':
    network = main(
        steps=5,
        activate_function=tl_activate,
        spawn_strategy=uniform_spawn_strategy(TLNode),
        nodes_number=4,
        p=0.1)
    print network
    nx.draw(network)
