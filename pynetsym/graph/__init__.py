import warnings

__all__ = ['IGraph', 'GraphError']

import traits.has_traits
traits.has_traits.CHECK_INTERFACES = 1
del traits

from .interface import IGraph
from .error import GraphError

try:
    import networkx
    del networkx
except ImportError:
    warnings.warn("NetworkX not installed.")
else:
    from nx_impl import NxGraph
    __all__.append('NxGraph')


try:
    import scipy.sparse
    del scipy
except ImportError:
    warnings.warn("Scipy not installed.")
else:
    from scipy_impl import ScipyGraph, DirectedScipyGraph
    __all__.append('ScipyGraph', 'DirectedScipyGraph')

del warnings