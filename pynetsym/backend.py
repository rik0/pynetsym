import types
import abc
import random
import pynetsym
import pynetsym.metautil
import pynetsym.rndutil

class GraphError(RuntimeError):
    pass

## TODO: rename as wrapper & add uniform access for the 'handle'
class GraphWrapper(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def handle(self):
        pass

    @abc.abstractmethod
    def add_node(self, identifier, agent):
        """
        Add specified node to the graph.
        @param identifier: the identifier of the node
        @type identifier: int
        @param agent: the agent
        """

    @abc.abstractmethod
    def add_edge(self, source, target):
        pass

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
        except GraphError:
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
    def remove_node(self, node):
        pass

    @abc.abstractmethod
    def __contains__(self, item):
        pass

    @abc.abstractmethod
    def __getitem__(self, item):
        pass

try:
    import networkx as nx
except ImportError, nx_import_exception:
    nx = types.ModuleType('networkx', 'Fake module')

    class NXGraphWrapper(GraphWrapper):
        def __init__(self):
            raise nx_import_exception
else:
    class NXGraphWrapper(GraphWrapper):
        def __init__(self):
            self.graph = nx.Graph()

        @property
        def handle(self):
            return self.graph

        ## TODO: move this towards a proper wrapper
        def random_node(self):
            """Draw a random node from the graph.

            Returns a node index or None if the graph has no nodes.

            Notice that it assumes that the graph nodes have indices going from 0 to some n.
            If it is not the case, the draw may not be uniform, bugs may arise, demons may
            fly out of your node.
            """
            ## TODO: this is wrong from a probabilistic point of view
            ## Fix it using additional data structures and for example a layer of indirection
            ## mapping each index with a single node
            try:
                max_value = self.graph.number_of_nodes()
                chosen_index = random.randrange(0, max_value)
            except ValueError:
                raise GraphError("Extracting node from empty graph.")
            else:
                if self.graph.has_node(chosen_index):
                    return chosen_index
                else:
                    return pynetsym.rndutil.choice_from_iter(
                        self.graph.nodes_iter(),
                        max_value)

        def add_edge(self, source, target):
            self.graph.add_edge(source, target)

        def random_edge(self):
            """
            Draw a random edge from the graph.

            Returns (node_id, node_id) pair or None if the graph has no edges.

            This is relatively safe, although horribly slow.
            """
            try:
                return pynetsym.rndutil.choice_from_iter(
                    self.graph.edges_iter(),
                    self.graph.number_of_edges())
            except ValueError:
                raise GraphError("Extracting edge from graph with no edges")

        def add_node(self, identifier, agent):
            self.graph.add_node(identifier, agent=agent)

        def remove_node(self, identifier):
            self.graph.remove_node(identifier)

        def __contains__(self, identifier):
            return identifier in self.graph

        def __getitem__(self, identifier):
            try:
                return self.graph.node[identifier]['agent']
            except KeyError:
                print '=' * 80
                print identifier
                print self.graph.node[identifier]
                print '=' * 80
                raise

try:
    import igraph
except ImportError, igraph_import_exception:
    igraph = types.ModuleType('igraph', 'Fake module')

    class IGraphWrapper(GraphWrapper):
        def __init__(self):
            raise igraph_import_exception
else:
    class IGraphWrapper(GraphWrapper):
        def __init__(self, graph):
            """
            Creates an implementation of Graph backed with igraph.Graph
            @param graph: the backing graph
            @type graph: igraph.Graph
            """
            self.graph = graph

        def add_node(self, identifier, agent):
            self.graph.add_vertices(1)
            largest_index = len(self.graph.vs) - 1
            self.graph.vs[largest_index]["identifier"] = identifier
            self.graph.vs[largest_index]["agent"] = agent


        def add_edge(self, source, target):
            source_node = self.dereference(source)
            target_node = self.dereference(target)
            self.graph.add_edges((source_node, target_node))

        def random_node(self):
            try:
                return random.choice(self.graph.vs).index
            except IndexError:
                raise GraphError("Extracting node from empty graph.")

        def random_edge(self):
            try:
                edge = random.choice(self.graph.es)
                return edge.source, edge.target
            except IndexError:
                raise GraphError("Extracting edge from graph with no edges")

        def dereference(self, identifier):
            nodes = self.graph.vs.select(identifier_eq=identifier)
            return nodes[0].index

        def remove_node(self, identifier):
            inner_identifier = self.dereference(identifier)
            self.graph.delete_vertices(inner_identifier)

