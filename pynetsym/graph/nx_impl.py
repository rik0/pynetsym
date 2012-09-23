from .import interface
import networkx as nx
from traits.api import Instance
from traits.api import DelegatesTo
from traits.api import implements
from ._abstract import AbstractGraph
from .error import GraphError


class NxGraph(AbstractGraph):
    implements(interface.IGraph)

    nx_graph = Instance(nx.Graph, allow_none=False)

    number_of_nodes = DelegatesTo('nx_graph')
    number_of_edges = DelegatesTo('nx_graph')
    has_edge = DelegatesTo('nx_graph')
    is_directed = DelegatesTo('nx_graph')

    neighbors = DelegatesTo('nx_graph')
    successors = DelegatesTo('nx_graph', prefix='neighbors')
    predecessors = DelegatesTo('nx_graph')

    def __init__(self, graph_type=nx.Graph, data=None, **kwargs):
        self.nx_graph = graph_type(data=data, **kwargs)
        if not self.is_directed():
            self.add_trait('predecessors',
                           DelegatesTo('nx_graph', prefix='neighbors'))

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

    def in_degree(self, node):
        if self.nx_graph.is_directed():
            return self.nx_graph.in_degree(node)
        else:
            return self.nx_graph.degree(node)

    def out_degree(self, node):
        if self.nx_graph.is_directed():
            return self.nx_graph.out_degree(node)
        else:
            return self.nx_graph.degree(node)

    def degree(self, node):
        return self.nx_graph.degree(node)

    def to_numpy(self, copy=False, minimize=False):
        return nx.to_numpy_matrix(self.nx_graph, dtype=bool)

    def to_nx(self, copy=False):
        if copy:
            return self.nx_graph.copy()
        else:
            return self.nx_graph

    def __contains__(self, node_index):
        return node_index in self.nx_graph

    def __iter__(self):
        return iter(self.nx_graph)

    def _valid_nodes(self, *nodes):
        for node in nodes:
            if node not in self.nx_graph:
                raise GraphError('%s node not in graph.' % node)

