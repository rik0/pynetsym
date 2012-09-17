from traits.api import Interface

class IGraph(Interface):
    def add_node(self, identifier):
        """
        Add specified node to the graph.
        @param identifier: the identifier of the node
        @type identifier: int
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