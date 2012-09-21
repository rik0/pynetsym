import unittest
import paramunittest
import itertools as it

import networkx as nx
from pynetsym.graph import NxGraph, ScipyGraph, GraphError, DirectedScipyGraph


undirected_graph_types = [(ScipyGraph, 100),
                          (NxGraph, )]
directed_graph_types = [(DirectedScipyGraph, 100),
                        (NxGraph, nx.DiGraph)]
all_graphs = undirected_graph_types + directed_graph_types

@paramunittest.parametrized(*all_graphs)
class TestEmptyGraph(unittest.TestCase):
    def setParameters(self, graph_factory, *args):
        self.graph = graph_factory(*args)

    def testEmpty(self):
        self.assertEqual(0, self.graph.number_of_nodes())
        self.assertEqual(0, self.graph.number_of_edges())

    def testAddedNode(self):
        self.assertEqual(0, self.graph.add_node())
        self.assertEqual(1, self.graph.number_of_nodes())
        self.assertEqual(0, self.graph.number_of_edges())

    def testDiad(self):
        self.assertEqual(0, self.graph.add_node())
        self.assertEqual(1, self.graph.add_node())
        self.graph.add_edge(0, 1)

        self.assertEqual(2, self.graph.number_of_nodes())
        self.assertEqual(1, self.graph.number_of_edges())

    def testDiadNoNodes(self):
        with self.assertRaises(GraphError):
            self.graph.add_edge(0, 1)

        self.assertEqual(0, self.graph.number_of_nodes())
        self.assertEqual(0, self.graph.number_of_edges())

    def testContains(self):
        self.assertFalse(0 in self.graph)
        self.graph.add_node()
        self.assert_(0 in self.graph)
        self.assertFalse(1 in self.graph)

        self.assertFalse(-1 in self.graph)
        self.assertFalse('foo' in self.graph)

    def testHasNode(self):
        self.assertFalse(self.graph.has_node(0))
        self.graph.add_node()
        self.assert_(self.graph.has_node(0))
        self.assertFalse(self.graph.has_node(1))

    def testHasNodeString(self):
        with self.assertRaises(ValueError):
            self.graph.has_node('foo')

    def testHasNodeNegative(self):
        with self.assertRaises(ValueError):
            self.graph.has_node(-1)

    def testRemove(self):
        with self.assertRaises(GraphError):
            self.graph.remove_edge(0, 1)

        self.graph.add_node()
        self.graph.add_node()

        with self.assertRaises(GraphError):
            self.graph.remove_edge(0, 1)


@paramunittest.parametrized(*it.product([5, 7, 10, 12], all_graphs))
class TestStarGraph(paramunittest.ParametrizedTestCase):
    def setParameters(self, size, construction_options):
        self.size = size
        graph_factory, args = construction_options[0], construction_options[1:]
        self.graph = graph_factory(*args)

    def setUp(self):
        for _ in xrange(self.size):
            self.graph.add_node()

        for node_index in xrange(1, self.size):
            self.graph.add_edge(0, node_index)

    def testStar(self):
        self.assertEqual(self.size-1, self.graph.number_of_edges())
        self.assertEqual(self.size, self.graph.number_of_nodes())

    def testRemoveEdge(self):
        self.graph.remove_edge(0, 1)
        self.assertEqual(self.size-2, self.graph.number_of_edges())
        self.assertEqual(self.size, self.graph.number_of_nodes())

    def testDoubleRemoveEdge(self):
        self.graph.remove_edge(0, 1)
        with self.assertRaises(GraphError):
            self.graph.remove_edge(0, 1)
        self.assertEqual(self.size-2, self.graph.number_of_edges())
        self.assertEqual(self.size, self.graph.number_of_nodes())

