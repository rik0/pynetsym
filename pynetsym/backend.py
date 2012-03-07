import abc
import random
import pynetsym
import pynetsym.rndutil

class Graph(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def add_node(self, identifier, attr_dict=None, **attr):
        """
        Add specified node to the graph.
        @param identifier: the identifier of the node
        @type identifier: int
        """

    @abc.abstractmethod
    def random_node(self):
        """
        Return a random node chosen uniformly.
        @return: a node
        @rtype: int
        """
        pass

    def preferential_attachment_node(self):
        """
        Return a random node chosen according to preferential attachment
        @return: a node
        @rtype: int
        """
        return self.random_edge()[0]

    @abc.abstractmethod
    def random_edge(self):
        """
        Return a random edge chosen uniformly
        @return: an edge
        @rtype: int, int
        """
        pass

try:
    import networkx as nx
except ImportError, e:
    nx = None
    class NXGraph(Graph):
        def __init__(self):
            raise ImportError("Could not find networkx")
else:
    class NXGraph(nx.Graph, Graph):
        def random_node(self):
            """Draw a random node from the graph.

            Returns a node index or None if the graph has no nodes.

            Notice that it assumes that the graph nodes have indices going from 0 to some n.
            If it is not the case, the draw may not be uniform, bugs may arise, demons may
            fly out of your node.
            """
            max_value = self.number_of_nodes()
            chosen_index = random.randrange(0, max_value)
            if self.has_node(chosen_index):
                return chosen_index
            else:
                return pynetsym.rndutil.choice_from_iter(
                    self.nodes_iter(),
                    max_value)

        def random_edge(self):
            """
            Draw a random edge from the graph.

            Returns (node_id, node_id) pair or None if the graph has no edges.

            This is relatively safe, although horribly slow.
            """
            return pynetsym.rndutil.choice_from_iter(
                self.edges_iter(),
                self.number_of_edges())



try:
    import igraph
except ImportError, e:
    igraph = None
    class IGraphWrapper(Graph):
        def __init__(self):
            raise ImportError("Could not find igraph")
else:
    class IGraphWrapper(Graph):
        def __init__(self, graph):
            """
            Creates an implementation of Graph backed with igraph.Graph
            @param graph: the backing graph
            @type graph: igraph.Graph
            """
            self.graph = graph

        def add_node(self, identifier, attr_dict=None, **attr):
            self.graph.add_vertices(1)
            largest_index = len(self.graph.vs) - 1
            self.graph.vs[largest_index]["identifier"] = identifier

        def random_node(self):
            return random.choice(self.graph.vs).index

        def random_edge(self):
            edge = random.choice(self.graph.es)
            return edge.source, edge.target
