
from traits.api import HasTraits, implements, Instance

from .interface import IGraph
from pynetsym import identifiers_manager

class AbstractGraph(HasTraits):
    implements(IGraph)

    index_store = Instance(identifiers_manager.IntIdentifierStore,
                           allow_none=False, args=())


    def has_node(self, node_index):
        node_index = int(node_index)
        if node_index >= 0:
            return node_index in self
        else:
            raise ValueError('%d is not a valid node index' % node_index)