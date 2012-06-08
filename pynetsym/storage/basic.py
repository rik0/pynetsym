from exceptions import RuntimeError, NotImplementedError
import abc
from pynetsym.metautil import delegate_all, delegate
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

    @abc.abstractmethod
    def random_node(self):
        """
        Return a random node chosen uniformly.
        @return: a node index
        @rtype: int
        """
        pass

    @abc.abstractmethod
    def random_nodes(self, how_many):
        """
        Return a sample of how_many nodes.
        """
        pass


    @abc.abstractmethod
    def preferential_attachment_node(self):
        """
        Return a random node chosen according to preferential attachment.
        @return a node index
        @rtype: int
        """
        pass

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
        @param keep_contacts: whether to remove or to update all the
            contacts that where associated with the old node.
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
        @rtype: pynetsym.core.Agent
        """

    @abc.abstractmethod
    def neighbors(self, node_identifier):
        """
        Return the neighbors of the specified node.
        """
        pass

    @abc.abstractmethod
    def nodes(self):
        """
        Return a collection of all the nodes in the network.
        """
        pass

    def number_of_nodes(self):
        """
        Return the number of nodes in the network.

        @warning: the default implementation is not efficient, as it calls self.nodes()
        """
        return len(self.nodes())

    def output_processor(self, processor, *additional_arguments):
        processor(self.handle, *additional_arguments)


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

    @notifies(ADD, NODE)
    @delegate
    def add_node(self, identifier, agent):
        pass

    @notifies(ADD, EDGE)
    @delegate
    def add_edge(self, source, target):
        pass

    @notifies(REMOVE, EDGE)
    @delegate
    def remove_egde(self, source, target):
        pass

    @notifies(REMOVE, NODE)
    @delegate
    def remove_node(self, identifier):
        pass

    @notifies(MODIFY, NODE)
    @delegate
    def switch_node(self, identifier, node, keep_contacts=False):
        pass
