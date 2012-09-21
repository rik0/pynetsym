from traits.api import Interface

class IGraph(Interface):
    def add_node(self):
        """
        Add a node to the graph.
        @return The index of the newly created node.
        @rtype int
        """

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
        pass

    def __contains__(self, identifier):
        """
        True if the graph contains the specified identifier.
        @param identifier: the identifier to seek
        @type identifier: int
        @return: True if identifier is in graph
        @rtype: bool
        """
        pass

    def neighbors(self, identifier):
        """
        Return the neighbors of the specified node.
        """
        pass

    def number_of_nodes(self):
        """
        Return the number of nodes in the network.

        @return: The number of edges in the network
        @rtype: int
        @warning: the default implementation is not efficient, as it calls self.nodes()
        """
        return len(self.nodes())

    def number_of_edges(self):
        """
        Return the number of edges in the network.
        @return: The number of edges in the network.
        @rtype: int
        """

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

    def to_scipy(self, copy=False):
        """
        Return corresponding NetworkX graph.
        @param copy: whether the graph should be copied.
        @type copy: bool
        @return: A scipy sparse matrix.
        @rtype: scipy.sparse.spmatrix

        @warning: depending from the actual kind of graph this may be a copy
          or the original one. Modifications to a graph that is not a copy
          may lead to servere malfunctions, unless the simulation has already
          stopped.
        """

    def to_numpy(self, copy=False):
        """
        Return corresponding NetworkX graph.
        @param copy: whether the graph should be copied.
        @type copy: bool
        @return: A numpy dense matrix.
        @rtype: numpy.ndarray

        @warning: depending from the actual kind of graph this may be a copy
          or the original one. Modifications to a graph that is not a copy
          may lead to servere malfunctions, unless the simulation has already
          stopped.
        """
