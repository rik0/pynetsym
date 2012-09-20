from scipy import sparse
from traits.api import HasTraits, implements, Callable, Instance
from traits.api import Int

from .interface import IGraph



class ScipyGraph(HasTraits):
    implements(IGraph)

    matrix_factory = Callable(sparse.lil_matrix)
    matrix = Instance(
            sparse.spmatrix, factory=matrix_factory,
            allow_none=False)
    max_nodes = Int(0)

    def __init__(self, max_nodes):
        self.matrix = self.matrix_factory(
            (max_nodes, max_nodes), dtype=bool)

    def add_node(self, node):
        assert node < self.max_nodes

    def add_edge(self, source, target):
        # consider direct vs. undirected
        self.matrix[source, target] = \
            self.matrix[target, source] = True

    def number_of_nodes(self):
        return self.matrix.shape[0]

    def number_of_edges(self):
        assert self.matrix.nnx % 2 == 0
        return self.matrix.nnz / 2

    def remove_edge(self, source, target):
        self.matrix[source, target] = \
            self.matrix[target, source] = False

class DirectedScipyGraph(ScipyGraph):
    def number_of_edges(self):
        return self.matrix.nnz

    def add_edge(self, source, target):
        self.matrix[source, target] = True

    def remove_edge(self, source, target):
          self.matrix[source, target] = False