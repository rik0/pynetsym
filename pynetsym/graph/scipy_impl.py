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

    _nodes = Set(Int)

    def _max_nodes(self):
        return self.matrix.shape[0]

    def __init__(self, max_nodes):
        self.matrix = self.matrix_factory(
            (max_nodes, max_nodes), dtype=bool)

    def add_node(self):
        node_index = self.index_store.take()
        if node_index >= self._max_nodes():
            self._enlarge(node_index)
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
        self.matrix[source, target] = \
            self.matrix[target, source] = False

    def __contains__(self, node_index):
        return node_index in self._nodes

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
        self.matrix[source, target] = False