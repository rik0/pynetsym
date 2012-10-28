import unittest
import paramunittest
from pynetsym.graph import ScipyGraph, NxGraph
import networkx as nx

@paramunittest.parametrized(
    (ScipyGraph, (12, )),
    (NxGraph, ())
)
class TestGraphExporting(paramunittest.ParametrizedTestCase):
    def setParameters(self, factory, arguments):
        self.factory = factory
        self.arguments = arguments

    def setUp(self):
        self.removed_node = 3
        self.number_of_initial_nodes = 5

        self.graph = self.factory(*self.arguments)
        self.graph.add_nodes(self.number_of_initial_nodes)
        for target in xrange(1, self.number_of_initial_nodes):
            self.graph.add_edge(0, target)

#        self.graph.remove_node(self.removed_node)

    def testNetworkX(self):
        expected_graph = nx.star_graph(self.number_of_initial_nodes - 1)
        self.assertTrue(nx.is_isomorphic(expected_graph, self.graph.to_nx()))