import collections
import numbers
from numpy import isscalar, ndarray
import functools as fc
import itertools as it

def identity(x):
    return x

def issequence(item):
    if (isinstance(item, collections.Sequence) or
        (isinstance(item, ndarray) and item.ndim == 1)):
        return True
    else:
        return False


class DefaultIndexMap(object):
    def __init__(self, dictionary={}, default_function=identity):
        if not all(isinstance(key, numbers.Integral) for key in dictionary.keys()):
            raise TypeError('Some key is not integral')
        self.elements = dict(dictionary)
        self.default_function = default_function

    def _get_one(self, item):
        if isinstance(item, numbers.Integral):
            try:
                return self.elements[item]
            except KeyError:
                try:
                    return self.default_function(item)
                except Exception as e:
                    raise KeyError(e)
        else:
            raise TypeError("Key %s is not an integer." % item)

    def __getitem__(self, item):
        if issequence(item):
            return [self._get_one(element) for element in item]
        elif isinstance(item, slice):
            max_value = max(item.start, -item.start, item.stop, -item.stop, *self.elements.keys())
            return [self._get_one(element) for element in xrange(*item.indices(max_value))]
        else:
            return self._get_one(item)