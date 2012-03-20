"""
Generic utility functions are defined here.

For example functions to manipulate primitive data types and such.
"""

import itertools as it
from heapq import heappop, heappush
from bisect import bisect_left

def subdict(dct, keys, on_error=None):
    """
    Return a subdictionary of dct that contains only the keys specified in keys
    @param dct: the original dictionary
    @type dct: dict
    @param keys: the sequence of keys to copy
    @param on_error: a function that is called if a key in keys is not in dct
        on_error(new_dict, dct, k)
    @return: the sub-dictionary
    @rtype: dict
    """

    d = type(dct)()
    for k in keys:
        try:
            d[k] = dct[k]
        except (KeyError, IndexError) as e:
            if on_error is not None:
                on_error(d, dct, k)
    return d

def splitdict(dct, keys):
    """
    Splits a dictionary in two dictionaries, one with the keys in @param keys
    one with the remaining keys.

    @param dct: the starting dictionary
    @type dct: dict
    @param keys: the keys to put in the first dictionary
    @type keys: iterable
    @return: A tuple of two dictionaries, the first containes the keys in
        @param keys
    @rtype: (dict, dict)
    """
    included = type(dct)()
    excluded = type(dct)()
    for k, v in dct.iteritems():
        if k in keys:
            included[k] = v
        else:
            excluded[k] = v
    return included, excluded


class IntIdentifierStore(object):
    """
    An free identifier store can be queried for the smallest free identifier.
    """

    def __init__(self):
        self._upper_identifier = 0
        self._holes = []

    def _clean_holes(self):
        self._holes = list(it.takewhile(
            lambda x: x < self._upper_identifier,
            self._holes))

    def peek(self):
        """
        Return the lowest available index
        @return: the lowest possible index
        @rtype: int
        """
        if self._holes:
            return heappop(self._holes)
        else:
            return self._upper_identifier

    def pop(self):
        """
        Return the lowest available index and marks it as used.
        @return: the lowest possible index
        @rtype: int
        """
        identifier = self.peek()
        self.mark(identifier)
        return identifier

    def _is_in_holes(self, identifier):
        if not self._holes:
            return False
        possible_index = bisect_left(self._holes, identifier)
        if self._holes[possible_index] == identifier:
            return True
        else:
            return False

    def _remove_from_holes(self, identifier):
        possible_index = bisect_left(self._holes, identifier)
        if self._holes[possible_index] == identifier:
            del self._holes[possible_index]

    def mark(self, identifier):
        """
        Marks the identifier as used
        @param identifier: the identifier to mark
        @type identifier: int
        @warning: NOP if identifier is not free
        """
        if self._is_in_holes(identifier):
            self._remove_from_holes(identifier)
            return identifier
        elif self._upper_identifier == identifier:
            self._upper_identifier += 1
            return identifier
        else:
            raise ValueError("Identifier %s was not free.", identifier)

    def unmark(self, identifier):
        """
        Frees the identifier.
        @param identifier: marks the identifier as free
        """
        if identifier < 0:
            raise ValueError(
                "Identifier should be > 0 (%s instead)" % identifier)
        elif (identifier < self._upper_identifier
              and not self._is_in_holes(identifier)):
            heappush(self._holes, identifier)
            self._try_regress_upper()

    def _try_regress_upper(self):
        while self._holes:
            if self._holes[-1] == self._upper_identifier - 1:
                del self._holes[-1]
                self._upper_identifier -= 1
            else:
                break
