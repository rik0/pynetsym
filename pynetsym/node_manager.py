import sys
from gevent.pool import Group
from traits.has_traits import Interface, implements
from traits.trait_types import List, Dict, Str, Instance

from pynetsym import core, metautil

import traits.api as t
from pynetsym.identifiers_manager import IntIdentifierStore
from pynetsym.util import extract_subdictionary, SequenceAsyncResult

__all__ = [
    'NodeManager',
    'Configurator',
    'IConfigurator',
    'BasicConfigurator'
]

class NodeManager(core.Agent):
    """
    The class responsible to create nodes.

    """
    name = 'manager'

    id_store = Instance(IntIdentifierStore, allow_none=False, args=())

    """
    the registered name in the L{address book<AddressBook>}
    """

    def __init__(self, graph):
        """
        Creates a new node_manager

        @param graph: the graph to pass to the agents
        @type graph: storage.GraphWrapper
        """
        self.graph = graph
        self.failures = []
        self.group = Group()

    # TODO: deal with returning identifiers.

    def fill_node(self, node):
        self.graph.add_node(node.id)
        node._greenlet.link_value(node._remove_from_network)
        node.graph = self.graph
        self.group.add(node._greenlet)

    def create_node(self, cls, parameters):
        """
        Creates a new node.

        @param cls: the factory creating the new node.
            Usually the node class.
        @type cls: callable
        @param parameters: the parameters that are forwarded to the node for
            creation
        @type parameters: dict
        @return: the actual identifier
        @rtype: int | str
        """
        node = cls(**parameters)
        identifier = self.id_store.pop()
        node.start(self._address_book, self._node_db, identifier)
        return identifier

    def simulation_ended(self):
        message = 'SIMULATION ENDED: REMAINING %d NODES.' % len(self.group)
        self.send_log(message)
        self.group.join()


class IConfigurator(Interface):
    def create_nodes(self):
        pass

    def create_edges(self):
        pass

    def do_initialize_nodes(self):
        pass

    @property
    def initialize_node(self):
        pass

class Configurator(core.Agent):
    implements(IConfigurator)

    name = 'configurator'

    initialize_nodes = False
    """
    When all the nodes are created, if the initialize_nodes attribute
    is set to true, all the nodes are sent an initialize message.
    Such attribute can be both set as a configurator_option
    or directly in the class like::

        class SomeSimulation(simulation.Simulation):
            class configurator(node_manager.BasicConfigurator):
                initialize = True
    """
    configurator_options = {}
    """
    Here we specify the names of the options for the configurator.
    Options are accumulated along the inheritance path
    """

    node_identifiers = List([])
    additional_arguments = Dict(key_trait=Str)

    def __init__(self, **additional_arguments):
        full_options = metautil.gather_from_ancestors(
                self, 'configurator_options')
        configurator_arguments = extract_subdictionary(
                additional_arguments, full_options)
        self.set(**configurator_arguments)
        self.set(additional_arguments=additional_arguments)

    def _start(self):
        self.create_nodes()
        self.create_edges()
        if self.initialize_nodes:
           self.do_initialization()

    def create_nodes(self):
        raise NotImplementedError()

    def create_edges(self):
        raise NotImplementedError()

    def do_initialization(self):
        for identifier in self.node_identifiers:
            self.send(identifier, 'initialize')

class BasicConfigurator(Configurator):
    """
    A BasicConfigurator needs a network_size parameter
    that specifies the size of the initial network.

    network_size nodes of type node_cls (specified in the body
    of the configurator) are created and are passed the arguments
    from additional_arguments specified in node_options.
    """
    configurator_options = {"starting_network_size"}
    starting_network_size = t.Int(1000)

    def node_cls(self):
        pass

    def node_options(self):
        return set()

    def create_edges(self):
        pass

    def create_nodes(self):
        self.node_arguments = extract_subdictionary(
                self.additional_arguments, self.node_options)
        node_ids = SequenceAsyncResult(
            [self.send(NodeManager.name, 'create_node',
                       cls=self.node_cls, parameters=self.node_arguments)
            for _r in xrange(self.starting_network_size)])
        self.node_identifiers = node_ids.get()


