import random
import networkx as nx
from pynetsym.core import Node, introduce_self_to_popular, tl_introduce

__author__ = 'enrico'

class TLNode(Node):
    def __init__(self, identifier, address_book,
                 graph, *args, **kwargs):
        self.p = kwargs.pop('death_probability')
        super(TLNode, self).__init__(
                identifier, address_book,
                graph, *args, **kwargs)


def tl_activate(node):
    graph = node.graph
    neighbors = nx.neighbors(graph, node.id)

    if len(neighbors) > 1:
        node_a, node_b = random.sample(neighbors, 2)
        node.send(node_a, tl_introduce(node_b))
        # if we have two friends that are connected, find new ones

    introduce_self_to_popular(node)