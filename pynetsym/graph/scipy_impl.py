from itertools import izip
import logging
from numpy import flatnonzero, fromiter, ix_
from scipy import sparse
from traits.api import implements, Callable, Instance


from .interface import IGraph
from ._abstract import AbstractGraph
from pynetsym.graph import GraphError, has

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

    def _remove_node_sure(self, node):
        self._nodes.remove(node)
        self.matrix[node,:] = False
        self.matrix[:, node] = False

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

    def neighbors(self, node):
        A = self.matrix.getrow(node).toarray()
        return flatnonzero(A).tolist()

    predecessors = neighbors
    successors = neighbors

    def degree(self, node):
        return self.matrix.getrow(node).nnz

    out_degree = degree
    in_degree = degree

    @property
    def ITN(self):
        nodes = fromiter(self._nodes, dtype=int,
                         count=len(self._nodes))
        nodes.sort()
        return nodes

    def to_numpy(self, minimize=False):
        if minimize:
            matrix, node_to_index, index_to_node = self.to_scipy(minimize=minimize)
            return matrix.todense(), node_to_index, index_to_node
        else:
            return self.to_scipy(minimize=minimize).todense()

    def to_nx(self, copy=False):
        if has('networkx'):
            import networkx
            return self._make_networkx(networkx.Graph())
        else:
            raise NotImplementedError()

    def _to_scipy_not_minimized(self, sparse_type):
        max_node = max(self._nodes) + 1
        M = self.matrix.tocoo()
        M._shape = (max_node, max_node)
        return M.asformat(sparse_type)

    def _sub_matrix(self, index_to_node, sparse_type):
        if sparse_type == 'csr':
            full_matrix_csc = self.matrix.tocsc()
            matrix_csr = full_matrix_csc[:, index_to_node].tocsr()
            return matrix_csr[index_to_node, :]
        else:
            full_matrix_csr = self.matrix.tocsr()
            matrix_csc = full_matrix_csr[index_to_node, :].tocsc()
            matrix = matrix_csc[:, index_to_node].asformat(sparse_type)
            return matrix

    def _to_scipy_minimized(self, sparse_type):
        index_to_node = self.ITN
        node_to_index = self.make_NTI(index_to_node)

        matrix = self._sub_matrix(index_to_node, sparse_type)
        return matrix, node_to_index, index_to_node

    def to_scipy(self, sparse_type=None, minimize=False):
        if sparse_type is None:
            sparse_type = self.matrix.getformat()
        if minimize:
            return self._to_scipy_minimized(sparse_type)
        else:
            return self._to_scipy_not_minimized(sparse_type)

    def __contains__(self, node_index):
        return node_index in self._nodes

    def __iter__(self):
        return iter(self._nodes)

    def _make_networkx(self, graph):
        graph.add_nodes_from(self._nodes)
        # not very efficient
        xs, ys = self.matrix.nonzero()
        graph.add_edges_from(izip(xs, ys))
        return graph

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

    def to_nx(self, copy=False):
        if has('networkx'):
            import networkx
            return self._make_networkx(networkx.DiGraph())
        else:
            raise NotImplementedError()