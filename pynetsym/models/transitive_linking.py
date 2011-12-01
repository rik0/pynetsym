import argparse
import random
import networkx as nx
import itertools as it
from .. import core, pa_utils

__author__ = 'enrico'

def make_parser(parent):
    parser = argparse.ArgumentParser(parents=[parent,])
    parser.add_argument('-n', '--network-size', default=100, type=int)
    parser.add_argument('--death-probability', default=0.01, type=float)
    return parser


def make_setup(network_size, death_probability):
    def setup(network_manager):
        generation_seed = it.izip(
            it.repeat(Node),
            xrange(network_size),
            it.repeat(dict(death_probability=death_probability)))
        for cls, identifier, node_params in generation_seed:
            network_manager.create_node(cls, identifier, node_params)

    return setup


class Node(core.Node):
    def __init__(self, identifier, address_book, graph, death_probability):
        self.death_probability = death_probability
        super(Node, self).__init__(identifier, address_book, graph)

    def activate(self):
        graph = self.graph
        neighbors = nx.neighbors(graph, self.id)

        if len(neighbors) > 1:
            node_a, node_b = random.sample(neighbors, 2)
            self.send(node_a, 'introduce_to', target_node=node_b)
        else:
            self.link_to(pa_utils.preferential_attachment)

    def introduce_to(self, target_node):
        graph = self.graph
        if graph.has_edge(self.id, target_node):
            return Node.introduction_failed
        else:
            self.send(target_node, Node.accept_link, originating_node=self.id)

    def introduction_failed(self):
        self.link_to(pa_utils.preferential_attachment)




