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

