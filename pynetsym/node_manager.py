import abc
import itertools as it
import sys

from pynetsym import core, util, metautil

class NodeManager(core.Agent):
    """
    The class responsible to create nodes.

    """
    name = 'manager' #: @ivar: the registered name in the L{address book<AddressBook>}

    def __init__(self, graph, address_book, configurator):
        super(NodeManager, self).__init__(NodeManager.name, address_book)
        self.graph = graph
        self.configurator = configurator

    def _run(self):
        if callable(self.configurator):
            self.configurator(self)
        else:
            self.configurator.setup(self)
        self.run_loop()

    def create_node(self, cls, identifier_hint, parameters):
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

        identifier = self._address_book.create_id_from_hint(identifier_hint)
        node = cls(identifier, self._address_book,
                   self.graph, **parameters)
        node.link_value(self.node_terminated_hook)
        node.link_exception(self.node_failed_hook)
        node.start()
        return 'created_node', dict(identifier=identifier)

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

    def __init__(self, **additional_arguments):
        self.activator_arguments = util.subdict(
            additional_arguments, self.activator_options)

    @metautil.classproperty
    def activator_options(self):
        pass

    @abc.abstractmethod
    def setup(self, node_manager):
        pass


class SingleNodeConfigurator(Configurator):
    def __init__(self, network_size, **additional_arguments):
        self.network_size = network_size
        self.node_arguments, additional_arguments = util.splitdict(
            additional_arguments, self.node_options )
        super(SingleNodeConfigurator, self).__init__(**additional_arguments)

    @property
    def identifiers_seed(self):
        return it.count()

    @metautil.classproperty
    def node_cls(self):
        pass

    @metautil.classproperty
    def node_options(self):
        pass

    def setup(self, node_manager):
        for identifier in it.islice(
            self.identifiers_seed, 0, self.network_size):
            node_manager.create_node(
                self.node_cls, identifier, self.node_arguments)
