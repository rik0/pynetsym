from traits.api import Interface, Enum, HasTraits, implements
from .error import GraphError
from .interface import IGraph
from ._util import function_to_map

import h5py

import traits.has_traits
traits.has_traits.CHECK_INTERFACES = 2

class BasicH5Graph(HasTraits):
    implements(IGraph)

    def __init__(self, h5_file):
        self.h5 = h5py.File(h5_file)
        self.indices = self.h5['indices']
        self.indptr = self.h5['indptr']

        self._added_nodes = 0

    def add_node(self):
        """
        Add a node to the graph.
        @return The index of the newly created node.
        @rtype int
        """
        self._added_nodes += 1
        if self._added_nodes == self.indptr.len():
            raise GraphError("Too many agents!")
        return self._added_nodes - 1


    def add_nodes(self, how_many):
        """
        Adds how_many nodes to the graph.
        @param how_many: The number of nodes to create
        @return: the sequence of indexes of the created nodes.
        """
        return [self.add_node() for _index in xrange(how_many)]

    def remove_node(self, node):
        """
        Removes the node "node" from the graph.
        @param node: the node to remove
        @return: None
        @raise ValueError: if the node is not in the graph.
        """
        raise GraphError("Cannot remove agents!")

    def add_edge(self, source, target):
        """
        Add edge to the graph

        @param source: the node from where the edge starts
        @type source: int
        @param target: the node to which the edge arrives
        @type target: int
        @warning: the actual behavior depends on the implementation being
            directed or undirected
        """
        raise GraphError('Cannot add or remove edges.')

    def remove_edge(self, source, target):
        """
        Removes edge from the graph

        @param source: the node from where the edge starts
        @type source: int
        @param target: the node to which the edge arrives
        @type target: int
        @warning: the actual behavior depends on the implementation being
            directed or undirected
        """
        raise GraphError('Cannot add or remove edges.')

    def __contains__(self, identifier):
        """
        True if the graph contains the specified identifier.
        @param identifier: the identifier to seek
        @type identifier: int
        @return: True if identifier is in graph
        @rtype: bool
        """
        if identifier < self._added_nodes:
            return True
        return False

    def __iter__(self):
        return xrange(self._added_nodes)

    def has_node(self, node_index):
        """
        True if the graph contains the specified identifier.
        @param identifier: the identifier to seek
        @type identifier: int
        @return: True if identifier is in graph
        @rtype: bool
        @raise ValueError: if identifier is not convertible to a non negative integer.
        """
        node_index = int(node_index)
        if node_index >= 0:
            return node_index in self
        else:
            raise ValueError('%d is not a valid node index' % node_index)

    def has_edge(self, source, target):
        """
        True if the graph contains the specified identifier.
        @param source: the node from where the edge starts
        @type source: int
        @param target: the node to which the edge arrives
        @type target: int
        @return: True if edge is in graph
        @rtype: bool
        @raise ValueError: if identifier is not convertible to a non negative integer.
        """
        return target in self.neighbors(source)

    def neighbors(self, node):
        """
        Return the neighbors of the specified node.
        @return: the neighbors
        @rtype: list
        """
        return self.indices[self.indptr[node]:self.indptr[node+1]]

    def successors(self, node):
        """
        Return the nodes that have an incoming edge from node.
        @return: the neighbors
        @rtype: list
        """
        return self.neighbors(node)

    def predecessors(self, node):
        """
        Return the nodes that have an outgoing edge to node.
        @return: the neighbors
        @rtype: list
        """
        return self.neighbors(node)

    def degree(self, node):
        """
        Return the degree of the specified node
        @param node: a node
        @return: the degree
        @rtype: int
        """
        return self.indptr[node+1] - self.indptr[node]

    def in_degree(self, node):
        """
        Return the in-degree of the specified node
        @param node: a node
        @return: the degree
        @rtype: int
        """
        return self.degree(node)

    def out_degree(self, node):
        """
        Return the out-degree of the specified node
        @param node: a node
        @return: the degree
        @rtype: int
        """
        return self.degree(node)

    def number_of_nodes(self):
        """
        Return the number of nodes in the network.

        @return: The number of edges in the network
        @rtype: int
        @warning: the default implementation is not efficient, as it calls self.nodes()
        """
        return self.indptr.len() - 1
        # return self._added_nodes

    def number_of_edges(self):
        """
        Return the number of edges in the network.
        @return: The number of edges in the network.
        @rtype: int
        """
        return self.indices.len()

    def is_directed(self):
        """
        Return true if the graph is directed.
        @return: True if the graph is directed, False otherwise.
        @rtype: bool
        """
        return False

    def node_to_index(self, node):
        """
        Return the progressive index of the node as if nodes where ordered.
        "Missing" values are skipped.

        @param node: the node
        @type node: int
        @return: the index
        @rtype: int
        @raise IndexError: if the required node is not in the matrix.
        """
        return node

    def index_to_node(self, index):
        """
        Returns the name of the nth node as specified by index.

        @param index: the index
        @type index: int
        @return: the node
        @rtype: int

        @warning: if the graph changed since when the index was created,
            the method is not an inverse for node_to_index anymore and
            creates wrong results.
        """
        return index

    def make_NTI(self, ITN=None):
        """
        Creates an NTI instance from an ITN instance.
        """
        return self.NTI

    @property
    def NTI(self):
        """
        An indexable object converting from nodes to indexes. See node_to_index.
        It also accepts some forms of advanced indexing.
        """
        return function_to_map(lambda x: x)

    @property
    def ITN(self):
        """
        An indexable object converting from indexes to nodes. See index_to_node.
        It also accepts some forms of advanced indexing.
        """
        return function_to_map(lambda x: x)


    def to_nx(self, copy=False):
        """
        Return corresponding NetworkX graph.
        @param copy: whether the graph should be copied.
        @type copy: bool
        @return: A networkx graph.
        @rtype: networkx.Graph

        @warning: depending from the actual kind of graph this may be a copy
          or the original one. Modifications to a graph that is not a copy
          may lead to servere malfunctions, unless the simulation has already
          stopped.
        """
        raise NotImplementedError()

    def to_scipy(self, sparse_type=None, minimize=False):
        """
        Return corresponding NetworkX graph.
        @param copy: whether the graph should be copied.
        @param sparse_type: the kind of sparse matrix that is returned
        @param minimize: whether we want the returned sparse matrix to be
          reshaped so that it contains only the minimum possible number
          of nodes. If False, the matrix can contain "empty" nodes before the
          maximum, however, no "empty" nodes remain after the last real node.
        @return: A scipy sparse matrix or, if minimize is requested, a tuple
            (matrix, node_to_index, index_to_node) where matrix is the
            sparse matrix with cols and rows corresponding to "nodes" not
            present in the network removed, node_to_index maps the node
            name to the corresponding matrix index and index_to_node makes
            the opposite.
        @rtype: scipy.sparse.spmatrix | (scipy.sparse.spmatrix, collections.Mapping, collections.Mapping)

        @warning: depending from the actual kind of graph this may be a copy
          or the original one. Modifications to a graph that is not a copy
          may lead to severe malfunctions, unless the simulation has already
          stopped.

          In general, if the type of sparse matrix requested is different from
          the underlying representation or if a minimization is requested, a copy
          is made.
        """
        if minimize==True:
            raise NotImplementedError()
        sparse_type = 'csr' if sparse_type is None else sparse_type
        indptr = np.array(self.indptr.shape, dtype=self.indptr.shape)
        self.indptr.read_direct(indptr)
        indices = np.array(self.indices.shape, dtype=self.indices.shape)
        self.indices.read_direct(indices)
        data = ones(self.indices.shape, dtype=np.int8)
        M = sparse.csr_matrix((data, indices, indptr),
            shape=(self.number_of_nodes, self.number_of_nodes))
        return M.asformat(sparse_type)

    def to_numpy(self, minimize=False):
        """
        Return corresponding NetworkX graph.
        @param minimize: determines if the returned matrix is as small
          as possible considering the nodes.
        @return: A numpy dense matrix.
        @rtype: numpy.ndarray | (scipy.sparse.spmatrix, numpy.ndarray, numpy.ndarray)

        @warning: depending from the actual kind of graph this may be a copy
          or the original one. Modifications to a graph that is not a copy
          may lead to severe malfunctions, unless the simulation has already
          stopped.
        """
        return self.to_scipy(
            sparse_type='csr',
            minimize=minimize).tolil().toarray()


    def apply(self, func, *args, **kwargs):
        """
        Applies func to the underlying graph representation as first argument.

        *args and **kwargs are passed as well.
        @return the value of the function call.
        """
        raise NotImplementedError()


    @property
    def handle(self):
        """
        Used to create a context:

            ```
            with graph.handle as handle:
                print clustering_coefficient(handle)
            ```
        """
        raise NotImplementedError()

    @property
    def handle_copy(self):
        """
        Used to create a context:

            ```
            with graph.handle_copy as handle:
                print clustering_coefficient(handle)
            ```
        """
        raise NotImplementedError()

    @property
    def random_selector(self):
        """
        Return a random selector.
        @return: the random selector.
        @rtype IRandomSelector
        """
        raise NotImplementedError()
