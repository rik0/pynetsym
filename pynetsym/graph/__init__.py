from pynetsym.util.plugin import conditional_from_import_into_exporting, require

__all__ = ['IGraph', 'GraphError']

import traits.has_traits

traits.has_traits.CHECK_INTERFACES = 1
del traits

from .interface import IGraph
from .error import GraphError


conditional_from_import_into_exporting('networkx',
                                       'pynetsym.graph.nx_impl',
                                       __name__,
                                       __all__,
                                       'NxGraph')

conditional_from_import_into_exporting('scipy.sparse',
                                       'pynetsym.graph.scipy_impl',
                                       __name__, __all__,
                                       'ScipyGraph', 'DirectedScipyGraph')

require('numpy')
