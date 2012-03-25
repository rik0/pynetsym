import abc
import sys

from pynetsym import core, util, metautil, argutils

class IdManager(object):
    """
    The IdManager is responsible to provide valid identifiers for Nodes.
    """
    def __init__(self):
        self.store = util.IntIdentifierStore()

    def get_identifier(self):
        """
        Get a new valid identifier.

        @return: the identifier
        @rtype: int
        """
        return self.store.pop()

    def node_added(self, event, kind, source, identifier, _node):
        self.store.mark(identifier)

    def node_removed(self, event, kind, source, identifier):
        self.free_identifier(identifier)

    def free_identifier(self, identifier):
        self.store.unmark(identifier)


class NodeManager(core.Agent):
    """
    The class responsible to create nodes.

    """
    name = 'manager' #: @ivar: the registered name in the L{address book<AddressBook>}

    def __init__(self, graph, address_book, id_manager, configurator):
        """
        Creates a new node_manager
        @param graph: the graph to pass to the agents
        @type graph: backend.GraphWrapper
        @param address_book: the address book to pass to the agents
        @type address_book: core.AddressBook
        @param id_manager: the source for nodes id
        @type id_manager: IdManager
        @param configurator: the configurator
        """
        super(NodeManager, self).__init__(NodeManager.name, address_book)
        self.graph = graph
        self.id_manager = id_manager
        self.configurator = configurator

    def _run(self):
        if callable(self.configurator):
            self.configurator(self)
        else:
            self.configurator.setup(self)
        self.run_loop()

    def create_node(self, cls, parameters):
        """
        Creates a new node.

        @param cls: the factory creating the new node. Usually the node class.
        @type cls: callable
        @param identifier_hint: the identifier to bind the new node to
        @type identifier_hint: int
        @param parameters: the parameters that are forwarded to the node for
            creation
        @type parameters: dict
        @return: the actual identifier
        @rtype: int | str
        """

        identifier = self.id_manager.get_identifier()
        try:
            node = cls(identifier, self._address_book,
                       self.graph, **parameters)
            node.link_value(self.node_terminated_hook)
            node.link_exception(self.node_failed_hook)
            node.start()
            return 'created_node', dict(identifier=identifier)
        except Exception as e:
            self.id_manager.free_identifier(identifier)
            return 'creation_failed', {'exception':e}

    def node_failed_hook(self, node):
        """
        Hooks an exception in the node. This implementation only prints stuff.

        @param node: the node that failed.
        @type node: Node
        """
        print >> sys.stderr, "Node failed: {}\n{}".format(node, node.exception)

    def node_terminated_hook(self, node):
        """
        Hooks a node termination. Usually nothing has to be done.

        @param node: the node that terminated.
        @type node: Node

        """
        pass


class Configurator(object):
    __metaclass__ = abc.ABCMeta

    configurator_options = {}
    """
    Here we specify the names of the options for the configurator.
    Options are accumulated along the inheritance path
    """

    def __init__(self, **additional_arguments):
        full_options = metautil.gather_from_ancestors(
                self, 'configurator_options')
        configurator_arguments = argutils.extract_options(
                additional_arguments, full_options)
        vars(self).update(configurator_arguments)
        self.additional_arguments = additional_arguments

    @abc.abstractmethod
    def setup(self, node_manager):
        pass

# TODO move in configurator the initialization stuff.
class SingleNodeConfigurator(Configurator):
    """
    A SingleNodeConfigurator needs a network_size parameter
    that specifies the size of the initial network.

    network_size nodes of type node_cls (specified in the body
    of the configurator) are created and are passed the arguments
    from additional_arguments specified in node_options.

    When all the nodes are created, if the initialize attribute
    is set to true, all the nodes are sent an initialize message.
    Such attribute can be both set as a configurator_option
    or directly in the class like::

        class SomeSimulation(simulation.Simulation):
            class configurator(node_manager.SingleNodeConfigurator):
                initialize = True
    """
    configurator_options = {"network_size"}
    initialize = False

    @metautil.classproperty
    def node_cls(self):
        pass

    @metautil.classproperty
    def node_options(self):
        pass

    def setup(self, node_manager):
        self.nodes = []
        self.node_arguments = argutils.extract_options(
                self.additional_arguments, self.node_options)
        for _ in xrange(self.network_size):
            node_manager.create_node(
                self.node_cls, self.node_arguments)
        if self.initialize:
            for identifier in self.nodes:
                node_manager.send(identifier, 'initialize')

    def node_created(self, identifier):
        self.nodes.append(identifier)
