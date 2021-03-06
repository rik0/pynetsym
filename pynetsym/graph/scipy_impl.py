from contextlib import contextmanager
from itertools import izip
import random
import numpy as np
from numpy import flatnonzero, fromiter, hstack, append
from scipy import sparse
from traits.api import implements, Callable, Instance
from traits.trait_types import DelegatesTo

from .interface import IGraph
from ._abstract import AbstractGraph
from pynetsym.graph import GraphError, has
from pynetsym.graph.random_selector import IRandomSelector, RepeatedNodesRandomSelector
from pynetsym.util import classproperty

class ScipyRandomSelector(RepeatedNodesRandomSelector):
    implements(IRandomSelector)

    nodes = DelegatesTo('graph_container', prefix='_nodes')
    matrix = DelegatesTo('graph_container')

    def random_node(self):
        return random.choice(list(self.nodes))

    def random_edge(self):
        index = random.randrange(0, self.matrix.nnz)
        rows, cols = self.matrix.nonzero()
        return rows[index], cols[index]

    def prepare_preferential_attachment(self):
        self.repeated_nodes = hstack(
            sparse.triu(self.matrix, format='coo').nonzero())
        self.repeated_nodes = append(self.repeated_nodes,
                                     fromiter(iter(self.nodes),
                                              dtype=np.int32),)
        self._initialized_preferential_attachment = True

class DirectedScipyRandomSelector(ScipyRandomSelector):
    def prepare_preferential_attachment(self):
        self.repeated_nodes = hstack(
            self.matrix.nonzero())
        self.repeated_nodes = append(self.repeated_nodes,
                                     fromiter(iter(self.nodes),
                                              dtype=np.int32),)
        self._initialized_preferential_attachment = True

class ScipyGraph(AbstractGraph):
    """
    Default wrapper for a Scipy Sparse Matrix.

    Using a Scipy sparse matrix as a backend, this
    implementation combines very good memory efficient
    and programming convenience.

    In order to make graph and network theoretic operations,
    it is relatively easy to obtain the network as a scipy
    sparse matrix in the right format for the efficient
    computation by means of the to_scipy method.

    Implementing algorithms as matrix computations is relatively
    straightforward.
    """
    implements(IGraph)

    matrix_factory = Callable(sparse.lil_matrix)
    matrix = Instance(
        sparse.spmatrix, factory=matrix_factory,
        allow_none=False)

    _nodes = Instance(set, args=())

    random_selector_factory = Callable(ScipyRandomSelector)

    def _max_nodes(self):
        return self.matrix.shape[0]

    @classproperty
    def parameters(self):
        return {}

    def __init__(self, max_nodes=None, matrix=None,
            nodes=None, random_selector=None):
        self.random_selector = (
                self.random_selector_factory(graph_container=self)
                    if random_selector is None else random_selector)
        if matrix is not None:
            self.matrix = matrix
            self.matrix_factory = type(matrix)
            if nodes is not None:
                self._nodes = nodes
            elif max_nodes is not None:
                max_nodes = min(max_nodes, matrix.shape[0])
                self._nodes = set(xrange(max_nodes))
            else:
                self._nodes = set(xrange(matrix.shape[0]))
        elif max_nodes is not None:
            self.matrix = self.matrix_factory(
                (max_nodes, max_nodes), dtype=bool)
        else:
            raise ValueError('Bad parameters %s' % (locals(), ))

    def add_node(self):
        node_index = self.index_store.take()
        if node_index >= self._max_nodes():
            self._enlarge(node_index)
            #heappush(self._nodes, node_index)
        self._nodes.add(node_index)
        self.random_selector.add_node(node_index)
        return node_index

    def _remove_node_sure(self, node):
        self._nodes.remove(node)
        self.matrix[node, :] = False
        self.matrix[:, node] = False
        self.random_selector.remove_node(node)

    def add_edge(self, source, target):
        self._valid_nodes(source, target)
        self.matrix[source, target] =\
        self.matrix[target, source] = True
        self.random_selector.add_edge(source, target)


    def number_of_nodes(self):
        return len(self._nodes)

    def number_of_edges(self):
        assert self.matrix.nnz % 2 == 0
        return self.matrix.nnz / 2

    def remove_edge(self, source, target):
        if self.matrix[source, target]:
            self.matrix[source, target] =\
            self.matrix[target, source] = False
            self.random_selector.remove_edge(source, target)
        else:
            raise GraphError(
                    'Edge %d-%d not present in graph' % (
                        source, target))

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
            matrix, node_to_index, index_to_node = self.to_scipy(
                    minimize=minimize)
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

    def apply(self, func, *args, **kwargs):
        return func(self.matrix, *args, **kwargs)

    @property
    @contextmanager
    def handle(self):
        yield self.matrix

    @property
    @contextmanager
    def handle_copy(self):
        yield self.matrix.copy()


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
    """
    Default wrapper for a Scipy Sparse Matrix representing a directed graph.
    """
    random_selector_factory = DirectedScipyRandomSelector

    def number_of_edges(self):
        return self.matrix.nnz

    def add_edge(self, source, target):
        self._valid_nodes(source, target)
        self.matrix[source, target] = True
        self.random_selector.add_edge(source, target)

    def remove_edge(self, source, target):
        self._valid_nodes(source, target)
        if self.matrix[source, target]:
            self.matrix[source, target] = False
            self.random_selector.remove_edge(source, target)
        else:
            raise GraphError(
                    'Edge %d-%d not present in graph' % (
                        source, target))

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


