from scipy import sparse
from traits.has_traits import HasTraits, implements

from .interface import IGraph


class ScipyGraph(HasTraits):
    implements(IGraph)

