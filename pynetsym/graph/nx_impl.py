from .import interface
import networkx as nx
from numpy import fromiter
from traits.api import Instance
from traits.api import implements
from ._abstract import AbstractGraph
from .error import GraphError


class NxGraph(AbstractGraph):
    implements(interface.IGraph)

    nx_graph = Instance(nx.Graph, allow_none=False)

    def __init__(self, graph_type=nx.Graph, data=None, **kwargs):
        self.nx_graph = graph_type(data=data, **kwargs)

    def add_node(self):
        node_index = self.index_store.take()
        self.nx_graph.add_node(node_index)
        return node_index

    def _remove_node_sure(self, node):
        self.nx_graph.remove_node(node)

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

    def node_to_index(self, node):
        return self.NTI[node]

    def index_to_node(self, index):
        return self.ITN[index]

    @property
    def NTI(self): # maybe pass optional ITN?
        pass


    @property
    def ITN(self):
        nodes = fromiter(self.nx_graph.nodes_iter(),
                         dtype=int,
                         count=self.nx_graph.number_of_nodes())
        nodes.sort()
        return nodes

    def to_numpy(self, minimize=False):
        return nx.to_numpy_matrix(self.nx_graph, dtype=bool)

    def to_nx(self, copy=False):
        if copy:
            return self.nx_graph.copy()
        else:
            return self.nx_graph

    def to_scipy(self, sparse_type=None, minimize=False):
        if minimize:
            raise NotImplementedError()
        return nx.to_scipy_sparse_matrix(self.nx_graph,
                                         format=sparse_type, dtype=bool)

    def predecessors(self, node):
        try:
            method = self.nx_graph.predecessors
        except AttributeError:
            return self.nx_graph.neighbors()
        else:
            return method(node)

    def neighbors(self, node):
        return self.nx_graph.neighbors(node)

    def successors(self, node):
        try:
            method = self.nx_graph.successors
        except AttributeError:
            return self.nx_graph.neighbors()
        else:
            return method(node)


    def number_of_nodes(self):
        return self.nx_graph.number_of_nodes()

    def number_of_edges(self):
        return self.nx_graph.number_of_edges()

    def has_edge(self, source, target):
        return self.nx_graph.has_edge(source, target)

    def is_directed(self):
        return self.nx_graph.is_directed()

    def __contains__(self, node_index):
        return node_index in self.nx_graph

    def __iter__(self):
        return iter(self.nx_graph)

    def _valid_nodes(self, *nodes):
        for node in nodes:
            if node not in self.nx_graph:
                raise GraphError('%s node not in graph.' % node)

