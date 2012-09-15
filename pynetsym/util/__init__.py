"""
Generic utility functions are defined here.

For example functions to manipulate primitive data types and such.
"""

__all__ = [
    'extract_subdictionary',
    'choice_from_iter',
    'SequenceAsyncResult',
    'encapsulate_global',
    'gather_from_ancestors',
    'classproperty'
]

try:
    import numpy
    del numpy
except ImportError:
    pass
else:
    from sna import ccdf, approximate_cpl, trivial_power_law_estimator, make_hist, degrees_to_hist
    __all__.extend([
        "ccdf",
        "approximate_cpl",
        "trivial_power_law_estimator",
        "make_hist",
        "degrees_to_hist"])

from dictionary import extract_subdictionary
from rnd import choice_from_iter
from concurrency import SequenceAsyncResult
from global_state import encapsulate_global
from meta import gather_from_ancestors, classproperty


