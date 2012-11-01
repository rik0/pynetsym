
from traits.api import HasTraits, implements, Instance

from .interface import IGraph
from pynetsym import identifiers_manager

class AbstractGraph(HasTraits):
    index_store = Instance(identifiers_manager.IntIdentifierStore,
                           allow_none=False, args=())

    def node_to_index(self, node):
        return self.NTI[node]

    def index_to_node(self, index):
        return self.ITN[index]

    def has_node(self, node_index):
        node_index = int(node_index)
        if node_index >= 0:
            return node_index in self
        else:
            raise ValueError('%d is not a valid node index' % node_index)

    def add_nodes(self, how_many):
        return [self.add_node() for _index in xrange(how_many)]

    def remove_node(self, node):
        if node in self:
            self._remove_node_sure(node)
        else:
            raise ValueError('Node %s not in the graph' % node)

    def _remove_node_sure(self, node):
        raise NotImplementedError()