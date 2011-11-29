import random
import networkx as nx
from .. import core

__author__ = 'enrico'

class TLNode(core.Node):
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
        node.send(node_a, core.tl_introduce(node_b))
        # if we have two friends that are connected, find new ones

    core.introduce_self_to_popular(node)