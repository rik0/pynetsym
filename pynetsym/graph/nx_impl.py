import random

from contextlib import contextmanager

import networkx as nx

from scipy import sparse
from numpy import fromiter, array
import numpy as np

from traits.api import Instance
from traits.api import implements
from traits.trait_types import DelegatesTo

from ._abstract import AbstractGraph
from .error import GraphError
from pynetsym.util import classproperty
from .random_selector import IRandomSelector, RepeatedNodesRandomSelector
from .import interface


class NxGraph(AbstractGraph):
    implements(interface.IGraph)

    nx_graph = Instance(nx.Graph, allow_none=False)

    @classproperty
    def parameters(self):
        return dict(graph=nx.Graph())

    def __init__(self, graph, random_selector=None):
        self.nx_graph = nx.Graph() if graph is None else graph
        self.random_selector = (NxRandomSelector(graph_container=self)
                                if random_selector is None else random_selector)

    def add_node(self):
        node_index = self.index_store.take()
        self.nx_graph.add_node(node_index)
        self.random_selector.add_node(node_index)
        return node_index

    # remove_node is defined in AbstractGraph

    def _remove_node_sure(self, node):
        self.nx_graph.remove_node(node)
        self.random_selector.remove_node(node)

    def add_edge(self, source, target):
        self._valid_nodes(source, target)
        self.nx_graph.add_edge(source, target)
        self.random_selector.add_edge(source, target)

    def remove_edge(self, source, target):
        try:
            self.nx_graph.remove_edge(source, target)
            self.random_selector.remove_edge(source, target)
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

    @property
    def ITN(self):
        nodes = fromiter(self.nx_graph.nodes_iter(),
                         dtype=int,
                         count=self.nx_graph.number_of_nodes())
        nodes.sort()
        return nodes

    def to_numpy(self, minimize=False):
        if minimize:
            matrix = nx.to_numpy_matrix(self.nx_graph, dtype=bool)
            index_to_node = self.ITN
            node_to_index = self.make_NTI(index_to_node)
            return matrix, node_to_index, index_to_node
        else:
            # FIXME: there is a scipy bug that bits when converting
            # boolean matrices from non-lil to dense.
            return self.to_scipy(
                minimize=minimize).tolil().todense()

    def to_nx(self, copy=False):
        if copy:
            return self.nx_graph.copy()
        else:
            return self.nx_graph

    def _to_scipy_minimize(self, sparse_type):
        matrix = nx.to_scipy_sparse_matrix(
            self.nx_graph, format=sparse_type, dtype=bool)
        index_to_node = self.ITN
        node_to_index = self.make_NTI(index_to_node)
        return matrix, node_to_index, index_to_node

    def _to_scipy_not_minimize(self, sparse_type):
        edges_array = array(self.nx_graph.edges(), dtype=int).T

        if self.nx_graph.is_directed():
            multiplier = 1
            sources = edges_array[0, :]
            targets = edges_array[1, :]
            max_node = max(self.nx_graph.nodes_iter())
            shape = max_node + 1, max_node + 1
        else:
            multiplier = 2
            sources = edges_array.flat
            targets = edges_array[::-1, :].flat
            shape = None

        M = sparse.coo_matrix(
            (type('.', (object, ),
                  {'__len__': lambda _: self.nx_graph.number_of_edges() * multiplier,
                   '__getitem__': lambda _, __: True})(),
             (sources, targets)),
            dtype=bool, shape=shape)

        return M.asformat(sparse_type)

    def to_scipy(self, sparse_type=None, minimize=False):
        if minimize:
            return self._to_scipy_minimize(sparse_type)
        else:
            return self._to_scipy_not_minimize(sparse_type)


    def predecessors(self, node):
        try:
            method = self.nx_graph.predecessors
        except AttributeError:
            return self.nx_graph.neighbors(node)
        else:
            return method(node)

    def neighbors(self, node):
        return self.nx_graph.neighbors(node)

    def successors(self, node):
        try:
            method = self.nx_graph.successors
        except AttributeError:
            return self.nx_graph.neighbors(node)
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

    def apply(self, func, *args, **kwargs):
        return func(self.nx_graph, *args, **kwargs)

    @property
    @contextmanager
    def handle(self):
        yield self.nx_graph

    @property
    @contextmanager
    def handle_copy(self):
        yield self.nx_graph.copy()

    def __contains__(self, node_index):
        return node_index in self.nx_graph

    def __iter__(self):
        return iter(self.nx_graph)

    def _valid_nodes(self, *nodes):
        for node in nodes:
            if node not in self.nx_graph:
                raise GraphError('%s node not in graph.' % node)


class NxRandomSelector(RepeatedNodesRandomSelector):
    implements(IRandomSelector)
    # FIXME: this can be made faster!

    graph = DelegatesTo('graph_container', prefix='nx_graph')

    def random_edge(self):
        return random.choice(self.graph.edges())

    def random_node(self):
        return random.choice(self.graph.nodes())


    def prepare_preferential_attachment(self):
        self.repeated_nodes = np.zeros(dtype=np.int32,
                                       shape=(self.graph.number_of_edges() * 2
                                              + self.graph.number_of_nodes()))
        degrees = nx.degree(self.graph)
        counter = 0
        for node, degree in degrees.iteritems():
            extraction_probability = degree + 1
            self.repeated_nodes[counter:counter + extraction_probability] = node
            counter += extraction_probability
        self._initialized_preferential_attachment = True



















