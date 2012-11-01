import collections
from numpy import fromiter, ndarray
from scipy import sparse

class function_to_map(object):
    def __init__(self, func):
        self.func = func

    def __getitem__(self, item):
        return self.func(item)

class IndexMapper(object):
    def __init__(self, index_map, max_field):
        if callable(index_map) and not isinstance(index_map, collections.Mapping):
            index_map = function_to_map(index_map)
        self.index_map = index_map
        self.max_index = max_field

    def __getitem__(self, item):
        if isinstance(item, slice):
            return self._get_item_iter(
                xrange(*item.indices(self.max_index)))
        elif isinstance(item, (collections.Sequence,
                                ndarray, sparse.spmatrix)):
            return self._get_item_iter(item)
        else:
            try:
                return self.index_map[item]
            except Exception:
                raise IndexError('Node %s not in graph' % item)

    def _get_item_iter(self, seq):
        def seq_generator():
            for el in seq:
                try:
                    yield self.index_map[el]
                except Exception:
                    pass
        return fromiter(seq_generator(), dtype=int)