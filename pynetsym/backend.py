import abc
import heapq
import bisect

class Graph(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def add_node(self, identifier, attr_dict=None, **attr):
        """
        Add specified node to the graph.
        @param identifier: the identifier of the node
        @type identifier: int
        @warning: other identifier types may be supported depending on the
            underlying graph implementation.
        @precondition: identifier in free_identifiers
        """

    @abc.abstractmethod
    def free_identifiers(self):
        """
        Return a collection of identifiers that are free at the moment.

        @warning: if nodes are added or removed between successive calls
            to free_identifiers, the returned collection may vary
        """



try:
    import networkx as nx
except ImportError, e:
    nx = None
    class NXGraph(Graph):
        def __init__(self):
            raise ImportError("Could not find networkx")
else:
    pass

try:
    import igraph
except ImportError, e:
    igraph = None
    class IGraph(Graph):
        pass
