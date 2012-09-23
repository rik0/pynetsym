import unittest
from numpy import ones, zeros
import paramunittest
import itertools as it

import networkx as nx
from pynetsym.graph import NxGraph, ScipyGraph, GraphError, DirectedScipyGraph, has, can_test


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

    def testDoubleAddEdge(self):
        self.assertEqual(0, self.graph.add_node())
        self.assertEqual(1, self.graph.add_node())
        self.graph.add_edge(0, 1)
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

    def testRemoveEdge(self):
        with self.assertRaises(GraphError):
            self.graph.remove_edge(0, 1)

        self.graph.add_node()
        self.graph.add_node()

        with self.assertRaises(GraphError):
            self.graph.remove_edge(0, 1)



class _AbstractStarGraph(object):
    def setParameters(self, size, construction_options):
        self.size = size
        graph_factory, args = construction_options[0], construction_options[1:]
        self.graph = graph_factory(*args)

    def _peripheral_nodes(self):
        return xrange(1, self.size)

    def setUp(self):
        for _ in xrange(self.size):
            self.graph.add_node()

        for node_index in self._peripheral_nodes():
            self.graph.add_edge(0, node_index)

@paramunittest.parametrized(*it.product([5, 7, 10, 12], all_graphs))
class TestStarGraph(_AbstractStarGraph, paramunittest.ParametrizedTestCase):
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

    def testToNumpy(self):
        A = self.graph.to_numpy()
        self.assertTupleEqual((self.size, self.size), A.shape)

@paramunittest.parametrized(*it.product([5, 7, 10, 12], directed_graph_types))
class TestStarDirected(_AbstractStarGraph, paramunittest.ParametrizedTestCase):
    def testHasEdges(self):
        for node in self._peripheral_nodes():
            self.assert_(self.graph.has_edge(0, node))
            self.assertFalse(self.graph.has_edge(node, 0))

    def testNeighbors(self):
        self.assertSequenceEqual(range(1, self.size), self.graph.neighbors(0))
        for node in self._peripheral_nodes():
            self.assertSequenceEqual([], self.graph.neighbors(node))

    def testPredecessors(self):
        self.assertSequenceEqual([], self.graph.predecessors(0))
        for node in self._peripheral_nodes():
            self.assertSequenceEqual([0], self.graph.predecessors(node))

    def testSuccessors(self):
        self.assertSequenceEqual(range(1, self.size), self.graph.successors(0))
        for node in self._peripheral_nodes():
            self.assertSequenceEqual([], self.graph.successors(node))

    def testDegree(self):
        for node in self.graph:
            self.assertEqual(self.graph.degree(node),
                             self.graph.in_degree(node) + self.graph.out_degree(node))

    def testInDegree(self):
        self.assertEqual(0, self.graph.in_degree(0))
        for node in self._peripheral_nodes():
            self.assertEqual(1, self.graph.in_degree(node))

    def testOutDegree(self):
        self.assertEqual(self.size-1, self.graph.out_degree(0))
        for node in self._peripheral_nodes():
            self.assertEqual(0, self.graph.out_degree(node))

    def testDegreeAndNeighbors(self):
        for node in self.graph:
            total_neighbors_num = len(self.graph.neighbors(node) +
                self.graph.predecessors(node))
            self.assertEqual(total_neighbors_num,
                             self.graph.degree(node))
            self.assertEqual(len(self.graph.successors(node)),
                             self.graph.out_degree(node))
            self.assertEqual(len(self.graph.predecessors(node)),
                             self.graph.in_degree(node))

    @unittest.skipUnless(*can_test('numpy'))
    def testToNumpyElements(self):
        from numpy import testing
        A = self.graph.to_numpy()
        B = zeros((self.size, self.size), dtype=bool)
        B[0, 1:] = True

        testing.assert_array_equal(B, A)

@paramunittest.parametrized(*it.product([5, 7, 10, 12], undirected_graph_types))
class TestStarUndirected(_AbstractStarGraph, paramunittest.ParametrizedTestCase):
    def testHasEdges(self):
        for node in self._peripheral_nodes():
            self.assert_(self.graph.has_edge(0, node))
            self.assert_(self.graph.has_edge(node, 0))

    def testNeighbors(self):
        self.assertSequenceEqual(range(1, self.size), self.graph.neighbors(0))
        for node in self._peripheral_nodes():
            self.assertSequenceEqual([0], self.graph.neighbors(node))

    def testPredecessors(self):
        self.assertSequenceEqual(range(1, self.size), self.graph.predecessors(0))
        for node in self._peripheral_nodes():
            self.assertSequenceEqual([0], self.graph.predecessors(node))

    def testSuccessors(self):
        self.assertSequenceEqual(range(1, self.size), self.graph.successors(0))
        for node in self._peripheral_nodes():
            self.assertSequenceEqual([0], self.graph.successors(node))

    def testDegree(self):
        for node in self.graph:
            self.assertEqual(self.graph.degree(node), self.graph.out_degree(node))
            self.assertEqual(self.graph.degree(node), self.graph.in_degree(node))

    def testInDegree(self):
        self.assertEqual(self.size-1, self.graph.in_degree(0))
        for node in self._peripheral_nodes():
            self.assertEqual(1, self.graph.in_degree(node))

    def testOutDegree(self):
        self.assertEqual(self.size-1, self.graph.out_degree(0))
        for node in self._peripheral_nodes():
            self.assertEqual(1, self.graph.out_degree(node))

    def testDegreeAndNeighbors(self):
        for node in self.graph:
            total_neighbors_num = len(self.graph.neighbors(node) +
                                self.graph.predecessors(node)) / 2
            self.assertEqual(total_neighbors_num,
                             self.graph.degree(node))
            self.assertEqual(len(self.graph.successors(node)),
                             self.graph.out_degree(node))
            self.assertEqual(len(self.graph.predecessors(node)),
                             self.graph.in_degree(node))

    @unittest.skipUnless(*can_test('numpy'))
    def testToNumpyElements(self):
        from numpy import testing
        A = self.graph.to_numpy()
        B = zeros((self.size, self.size), dtype=bool)
        B[0, 1:] = True
        B[1:, 0] = True

        testing.assert_array_equal(B, A)