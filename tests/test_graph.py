import unittest
import paramunittest

from pynetsym.graph import NxGraph, ScipyGraph, GraphError


@paramunittest.parametrized(
    (ScipyGraph, 100),
    (NxGraph, )
)
class TestGraph(unittest.TestCase):

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

