from bisect import bisect_left
from heapq import heappop, heappush
import itertools as it

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

    def take(self):
        """
        Return the lowest available index and marks is as used.
        @return: the lowest possible index
        @rtype: int
        """
        if self._holes:
            return heappop(self._holes)
        else:
            tmp = self._upper_identifier
            self._upper_identifier += 1
            return tmp

    def peek(self):
        """
        Return the lowest available index.
        @return: the lowest possible index
        @rtype: int
        """
        if self._holes:
            return self._holes[0]
        else:
            return self._upper_identifier

    def _is_in_holes(self, identifier):
        if not self._holes:
            return False
        possible_index = bisect_left(self._holes, identifier)
        if (possible_index < len(self._holes)
            and self._holes[possible_index] == identifier):
            return True
        else:
            return False

    def free(self, identifier):
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
        while self._holes and self._holes[-1] == self._upper_identifier - 1:
            del self._holes[-1]
            self._upper_identifier -= 1


