from  . import interface
import networkx as nx
from traits.api import HasTraits, Instance
from traits.api import DelegatesTo
from traits.has_traits import implements
from ._abstract import AbstractGraph
from .error import GraphError


class NxGraph(AbstractGraph):
    implements(interface.IGraph)


    nx_graph = Instance(nx.Graph, allow_none=False)

    number_of_nodes = DelegatesTo('nx_graph')
    number_of_edges = DelegatesTo('nx_graph')


    def __init__(self, graph_type=nx.Graph, data=None, **kwargs):
        self.nx_graph = graph_type(data=data, **kwargs)

    def add_node(self):
        node_index = self.index_store.take()
        self.nx_graph.add_node(node_index)
        return node_index

    def add_edge(self, source, target):
        self._valid_nodes(source, target)
        self.nx_graph.add_edge(source, target)

    def remove_edge(self, source, target):
        try:
            self.nx_graph.remove_edge(source, target)
        except nx.NetworkXError as e:
            raise GraphError(e)

    def __contains__(self, node_index):
        return node_index in self.nx_graph

    def _valid_nodes(self, *nodes):
        for node in nodes:
            if node not in self.nx_graph:
                raise GraphError('%s node not in graph.' % node)

