import random
import networkx as nx
from .. import core
from pynetsym.core import  make_accept_link, introduce_self_to_popular

__author__ = 'enrico'

class Node(core.Node):
    def __init__(self, identifier, address_book,
                 graph, *args, **kwargs):
        self.p = kwargs.pop('death_probability')
        super(Node, self).__init__(
                identifier, address_book,
                graph, *args, **kwargs)

def activate(node):
    graph = node.graph
    neighbors = nx.neighbors(graph, node.id)

    if len(neighbors) > 1:
        node_a, node_b = random.sample(neighbors, 2)
        node.send(node_a, make_introduce(node_b))
        # if we have two friends that are connected, find new ones

    core.introduce_self_to_popular(node)

def make_introduce(target_node):
    def introduce(node):
        graph = node.graph
        if graph.has_edge(node.id, target_node):
            return introduction_failed
        else:
            node.send(target_node, make_accept_link(node.id))
    return introduce


def introduction_failed(node):
    introduce_self_to_popular(node)