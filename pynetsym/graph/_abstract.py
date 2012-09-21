
from traits.api import HasTraits, implements, Instance

from .interface import IGraph
from pynetsym import identifiers_manager

class AbstractGraph(HasTraits):
    implements(IGraph)

    index_store = Instance(identifiers_manager.IntIdentifierStore,
                           allow_none=False, args=())