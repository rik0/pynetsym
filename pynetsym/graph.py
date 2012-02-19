import abc
import networkx as nx
import heapq
import bisect

from pynetsym import metautil

#@metautil.extract_interface(nx.Graph)
class Graph(object):
    """
    Abstract base class for graphs supporting the networkx.Graph interface.

    """
    __metaclass__ = abc.ABCMeta

###    nx.Graph.add_cycle                nx.Graph.copy                     nx.Graph.nbunch_iter              nx.Graph.remove_edges_from
###    nx.Graph.add_edge                 nx.Graph.degree                   nx.Graph.neighbors                nx.Graph.remove_node
###    nx.Graph.add_edges_from           nx.Graph.degree_iter              nx.Graph.neighbors_iter           nx.Graph.remove_nodes_from
###    nx.Graph.add_node                 nx.Graph.edges                    nx.Graph.nodes                    nx.Graph.selfloop_edges
###    nx.Graph.add_nodes_from           nx.Graph.edges_iter               nx.Graph.nodes_iter               nx.Graph.size
###    nx.Graph.add_path                 nx.Graph.get_edge_data            nx.Graph.nodes_with_selfloops     nx.Graph.subgraph
###    nx.Graph.add_star                 nx.Graph.has_edge                 nx.Graph.number_of_edges          nx.Graph.to_directed
###    nx.Graph.add_weighted_edges_from  nx.Graph.has_node                 nx.Graph.number_of_nodes          nx.Graph.to_undirected
###    nx.Graph.adjacency_iter           nx.Graph.is_directed              nx.Graph.number_of_selfloops
###    nx.Graph.adjacency_list           nx.Graph.is_multigraph            nx.Graph.order
###    nx.Graph.clear                    nx.Graph.mro                      nx.Graph.remove_edge

class AdjacencyMatrixGraph(Graph):
    def __init__(self):
        self._nodes = []
        self._edges = []

    def add_node(self, node, **attrs):
        index = bisect.bisect_left(self._nodes, node)
        if not self._nodes[index] != node:
            heapq.heappush(self._nodes, node)

    def nodes(self):
        return self._nodes.copy()

    def add_edge(self, start, end):
        index = bisect.bisect_left(self._edges, (start, end))
        if self._edges[index] != (start, end):
            self.add_node(start)
            self.add_node(end)
            heapq.heappush(self._edges, (start, end))
