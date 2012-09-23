from heapq import heappush
from numpy import flatnonzero, ix_
from scipy import sparse
from traits.api import HasTraits, implements, Callable, Instance
from traits.api import Int
from traits.trait_types import Set

from .interface import IGraph
from ._abstract import AbstractGraph
from pynetsym.graph import GraphError


class ScipyGraph(AbstractGraph):
    implements(IGraph)

    matrix_factory = Callable(sparse.lil_matrix)
    matrix = Instance(
            sparse.spmatrix, factory=matrix_factory,
            allow_none=False)

    _nodes = Instance(set, args=())

    def _max_nodes(self):
        return self.matrix.shape[0]

    def __init__(self, max_nodes):
        self.matrix = self.matrix_factory(
            (max_nodes, max_nodes), dtype=bool)

    def add_node(self):
        node_index = self.index_store.take()
        if node_index >= self._max_nodes():
            self._enlarge(node_index)
        #heappush(self._nodes, node_index)
        self._nodes.add(node_index)
        return node_index

    def add_edge(self, source, target):
        # consider direct vs. undirected
        self._valid_nodes(source, target)
        self.matrix[source, target] = \
            self.matrix[target, source] = True

    def number_of_nodes(self):
        return len(self._nodes)

    def number_of_edges(self):
        assert self.matrix.nnz % 2 == 0
        return self.matrix.nnz / 2

    def remove_edge(self, source, target):
        if self.matrix[source, target]:
            self.matrix[source, target] = \
                self.matrix[target, source] = False
        else:
            raise GraphError('Edge %d-%d not present in graph' % (source, target))

    def has_edge(self, source, target):
        self._valid_nodes(source, target)
        return self.matrix[source, target]

    def is_directed(self):
        return False

    def neighbors(self, identifier):
        A = self.matrix.getrow(identifier).toarray()
        return flatnonzero(A).tolist()

    predecessors = neighbors
    successors = neighbors

    def degree(self, node):
        return self.matrix.getrow(node).nnz

    out_degree = degree
    in_degree = degree

    def to_numpy(self, copy=False, minimize=False):
        A = self.matrix.toarray()
        node_list = list(self._nodes)
        return A[ix_(node_list, node_list)].copy()

    def __contains__(self, node_index):
        return node_index in self._nodes

    def __iter__(self):
        return iter(self._nodes)

    def _enlarge(self, node_index):
        self.matrix.reshape((node_index, node_index))

    def _valid_nodes(self, *nodes):
        for node in nodes:
            if node not in self._nodes:
                raise GraphError('%s node not in graph.' % node)




class DirectedScipyGraph(ScipyGraph):
    def number_of_edges(self):
        return self.matrix.nnz

    def add_edge(self, source, target):
        self._valid_nodes(source, target)
        self.matrix[source, target] = True

    def remove_edge(self, source, target):
        self._valid_nodes(source, target)
        if self.matrix[source, target]:
            self.matrix[source, target] = False
        else:
            raise GraphError('Edge %d-%d not present in graph' % (source, target))

    def is_directed(self):
        return True

    def predecessors(self, identifier):
        A = self.matrix.getcol(identifier).toarray()
        return flatnonzero(A).tolist()

    def degree(self, node):
        return self.in_degree(node) + self.out_degree(node)

    def in_degree(self, identifier):
        return self.matrix.getcol(identifier).nnz