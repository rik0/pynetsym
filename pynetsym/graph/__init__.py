import warnings

__all__ = ['IGraph', 'GraphError', 'can_test', 'has']

import traits.has_traits
traits.has_traits.CHECK_INTERFACES = 1
del traits

from .interface import IGraph
from .error import GraphError
from ._plugin import has, can_test, register

try:
    import networkx
    del networkx
except ImportError:
    warnings.warn("NetworkX not installed.")
else:
    from nx_impl import NxGraph
    __all__.append('NxGraph')
    register('networkx')

try:
    import scipy.sparse
    del scipy
except ImportError:
    warnings.warn("Scipy not installed.")
else:
    from scipy_impl import ScipyGraph, DirectedScipyGraph
    __all__.extend(['ScipyGraph', 'DirectedScipyGraph'])
    register('scipy')

try:
    import numpy
    del numpy
except ImportError:
    warnings.warn("Numpy not installed.")
else:
    register('numpy')


del warnings, register