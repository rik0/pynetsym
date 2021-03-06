from traits.has_traits import implements
from traits.trait_types import Dict, Str, Int, Any, Type, Set, false

from .. import core
from ..util import extract_sub_dictionary, SequenceAsyncResult
from ..node_manager import NodeManager
from .interface import IConfigurator

class AbstractConfigurator(core.Agent):
    implements(IConfigurator)

    name = 'configurator'

    options = {"full_parameters"}
    """
    Here we specify the names of the options for the configurator.
    Options are accumulated along the inheritance path
    """


    node_identifiers = Any
    full_parameters = Dict(key_trait=Str)

    def _start(self):
        self.create_nodes()
        self.create_edges()
        self.initialize_nodes()

    def create_nodes(self):
        raise NotImplementedError()

    def create_edges(self):
        raise NotImplementedError()

    def do_initialize(self):
        for identifier in self.node_identifiers:
            self.send(identifier, 'initialize')

    def do_not_initialize(self):
        pass

    initialize_nodes = do_not_initialize


class BasicConfigurator(AbstractConfigurator):
    """
    A BasicConfigurator needs a network_size parameter
    that specifies the size of the initial network.

    network_size nodes of type node_type (specified in the body
    of the configurator) are created and are passed the arguments
    from additional_arguments specified in node_options.
    """
    options = {"starting_network_size"}
    starting_network_size = Int(1000)

    node_type = Type
    node_options = Set(Str)

    def create_edges(self):
        pass

    def create_nodes(self):
        self.node_arguments = extract_sub_dictionary(
                self.full_parameters, self.node_options)
        node_ids = SequenceAsyncResult(
            [self.send(NodeManager.name, 'create_node',
                       cls=self.node_type, parameters=self.node_arguments)
            for _r in xrange(self.starting_network_size)])
        self.node_identifiers = node_ids.get()