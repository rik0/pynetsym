import argparse
import random
import itertools as it
from .. import core, rnd

__author__ = 'enrico'

class Node(core.Node):
    MAX_TRIALS = 10

    def __init__(self, identifier, address_book, graph, death_probability):
        self.death_probability = death_probability
        self.criterion = rnd.random_node
        super(Node, self).__init__(identifier, address_book, graph)

    def introduction(self):
        graph = self.graph
        neighbors = graph.neighbors(self.id)
        if len(neighbors) > 1:
            for _ in xrange(Node.MAX_TRIALS):
                node_a, node_b = random.sample(neighbors, 2)
                if not graph.has_edge(node_a, node_b):
                    self.send(node_a, 'introduce_to', target_node=node_b)
                    break
            else:
                self.link_to(self.criterion)
        else:
            self.link_to(self.criterion)

    def activate(self):
        if random.random() < self.death_probability:
            self.regenerate()
        else:
            self.introduction()


    def introduce_to(self, target_node):
        self.send(target_node, 'accept_link', originating_node=self.id)

    def regenerate(self):
        self.graph.remove_node(self.id)
        target_node = rnd.random_node(self.graph)
        self.link_to(target_node)

def make_parser(parent):
    parser = argparse.ArgumentParser(parents=[parent,])
    parser.add_argument('-n', '--network-size', default=100, type=int)
    parser.add_argument('--death-probability', default=0.01, type=float)
    return parser

def make_setup(network_size, death_probability, node_cls=Node):
    def setup(network_manager):
        generation_seed = it.izip(
            it.repeat(node_cls),
            xrange(network_size),
            it.repeat(dict(death_probability=death_probability)))
        for cls, identifier, node_params in generation_seed:
            network_manager.create_node(cls, identifier, node_params)

    return setup




