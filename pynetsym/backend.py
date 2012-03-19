import types
import abc
import random
import pynetsym
import pynetsym.metautil
import pynetsym.rndutil
import pynetsym.core

from pynetsym.metautil import delegate, delegate_all
from pynetsym.notifyutil import notifier, notifies

class GraphError(RuntimeError):
    pass

class GraphWrapper(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def handle(self):
        """
        A handle we can use to obtain the underlying graph.
        @warning: The actual type of the graph depends from the actual
            wrapper.
        """
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
        """
        Add edge to the graph

        @param source: the node from where the edge starts
        @type source: int
        @param target: the node to which the edge arrives
        @type target: int
        @warning: the actual behavior depends on the implementation being
            directed or undirected
        """
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


@notifier
@delegate_all(GraphWrapper, 'delegate', include_specials=True)
class NotifyingGraphWrapper(GraphWrapper):
    ADD = 'add'
    REMOVE = 'remove'
    MODIFY = 'modify'

    NODE = 'node'
    EDGE = 'edge'

    def __init__(self, delegate):
        self.delegate = delegate

    @delegate
    @notifies(ADD, NODE)
    def add_node(self, identifier, agent):
        pass

    @delegate
    @notifies(ADD, EDGE)
    def add_edge(self, source, target):
        pass

    @delegate
    @notifies(REMOVE, NODE)
    def remove_node(self, identifier):
        pass

    @delegate
    @notifies(MODIFY, NODE)
    def switch_node(self, identifier, node, keep_contacts=False):
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

        ## TODO: make it as atomic as possible
        def random_node(self):
            """
            Draw a random node from the graph.

            @return: a node index
            @rtype: int
            @raise GraphError if the graph is empty.

            @warning: notice that it assumes that the graph nodes have indices
            going from 0 to some n. If it is not the case, the draw may not be
            uniform, bugs may arise, demons may fly out of your node.
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

            @return: a pair of nodes representing an edge
            @rtype: (int, int)
            @raise GraphError: if the graph has no edges.

            @warning: this is relatively safe, although horribly slow.
            """
            try:
                return pynetsym.rndutil.choice_from_iter(
                    self.graph.edges_iter(),
                    self.graph.number_of_edges())
            except ValueError:
                raise GraphError("Extracting edge from graph with no edges")

        def add_node(self, identifier, agent):
            self.graph.add_node(identifier, agent=agent)
            with pynetsym.core.AgentIdUpdatableContext():
                agent.id = identifier

        def remove_node(self, identifier):
            self.graph.remove_node(identifier)

        def __contains__(self, identifier):
            return identifier in self.graph

        def __getitem__(self, identifier):
            return self.graph.node[identifier]['agent']

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

        def __getitem__(self, identifier):
            return self.graph.vs[identifier]["agent"]

        def add_edge(self, source, target):
            self.graph.add_edges((source, target))

        def random_node(self):
            try:
                return random.randrange(0, len(self.graph.vs))
            except IndexError:
                raise GraphError("Extracting node from empty graph.")

        def random_edge(self):
            try:
                edge = random.choice(self.graph.es)
                return edge.source, edge.target
            except IndexError:
                raise GraphError("Extracting edge from graph with no edges")

        def remove_node(self, identifier):
            raise NotImplementedError()

        @property
        def handle(self):
            return self.graph

        def __contains__(self, identifier):
            if 0 < identifier < len(self.graph.vs):
                return True
            else:
                return False
