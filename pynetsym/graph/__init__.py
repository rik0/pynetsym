import warnings

__all__ = ['IGraph']

from .interface import IGraph

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
    from scipy_impl import ScipyGraph
    __all__.append('ScipyMatrix')

del warnings