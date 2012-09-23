import warnings

__all__ = ['IGraph', 'GraphError']

import traits.has_traits
traits.has_traits.CHECK_INTERFACES = 1
del traits

from .interface import IGraph
from .error import GraphError


class _RegisteredPlugins:
    _plugins = set()

    @classmethod
    def has(cls, what):
        return what in cls._plugins

    @classmethod
    def can_test(cls, what):
        return what in cls._plugins, 'Missing module %s' % what

    @classmethod
    def register(cls, what):
        cls._plugins.add(what)

try:
    import networkx
    del networkx
except ImportError:
    warnings.warn("NetworkX not installed.")
else:
    from nx_impl import NxGraph
    __all__.append('NxGraph')
    _RegisteredPlugins.register('networkx')

try:
    import scipy.sparse
    del scipy
except ImportError:
    warnings.warn("Scipy not installed.")
else:
    from scipy_impl import ScipyGraph, DirectedScipyGraph
    __all__.extend(['ScipyGraph', 'DirectedScipyGraph'])
    _RegisteredPlugins.register('scipy')

try:
    import numpy
    del numpy
except ImportError:
    warnings.warn("Numpy not installed.")
else:
    _RegisteredPlugins.register('numpy')


has = _RegisteredPlugins.has
can_test = _RegisteredPlugins.can_test

del warnings