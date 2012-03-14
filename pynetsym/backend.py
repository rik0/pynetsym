import abc
import random
import pynetsym
import pynetsym.metautil
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
        try:
            return self.random_edge()[0]
        except ValueError:
            ## Means that random_edge failed: no edges all nodes
            ## have 0 degree!
            return self.random_node()

    @abc.abstractmethod
    def random_edge(self):
        """
        Return a random edge chosen uniformly
        @return: an edge
        @rtype: int, int
        """
        pass

    @abc.abstractmethod
    def remove_node(self, identifier):
        """
        Removes the specified node from the graph.
        @param identifier: the identifier of the node to remove.
        """
        pass

    def switch_node(self, identifier, node, keep_contacts=False):
        """
        Rebinds a node in the graph.

        @param identifier: the identifier to rebind the graph to
        @type identifier: int
        @param node: the new node
        @type pynetsym.core.Node
        @param keep_contacts: whether to remove or to update all the contacts
            that where associated with the old node.
        @warning: Currently keep_contacts is not supported
        """
        if keep_contacts:
            raise NotImplementedError()
        else:
            self.remove_node(identifier)
            self.add_node(identifier=identifier, agent=node)

    @abc.abstractmethod
    def __contains__(self, identifier):
        """
        True if the graph contains the specified identifier.
        @param identifier: the identifier to seek
        @type identifier: int
        @return: True if identifier is in graph
        @rtype: bool
        """
        pass

    @abc.abstractmethod
    def __getitem__(self, identifier):
        """
        Get the actual agent object with specified identifier.
        @param identifier: the identifier
        @type identifier: int
        @return: the agent
        @rtype: pynetsym.core.AbstractAgent
        """

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
            """
            Draw a random node from the graph.

            @return: a node index
            @rtype: int
            @raise IndexError if the graph is empty.

            @warning: notice that it assumes that the graph nodes have indices
            going from 0 to some n. If it is not the case, the draw may not be
            uniform, bugs may arise, demons may fly out of your node.
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

            @return: a pair of nodes representing an edge
            @rtype: (int, int)
            @raise IndexError: if the graph has no edges.

            @warning: this is relatively safe, although horribly slow.
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

        def add_edge(self, source, target):
            source_node = self.dereference(source)
            target_node = self.dereference(target)
            self.graph.add_edges((source_node, target_node))

        def random_node(self):
            return random.choice(self.graph.vs).index

        def random_edge(self):
            edge = random.choice(self.graph.es)
            return edge.source, edge.target

        def dereference(self, identifier):
            nodes = self.graph.vs.select(identifier_eq=identifier)
            return nodes[0].index

        def remove_node(self, identifier):
            inner_identifier = self.dereference(identifier)
            self.graph.delete_vertices(inner_identifier)

