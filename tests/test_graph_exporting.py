import unittest
from unittest import skip
from numpy import testing, array
import numpy as np
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

        self.graph.remove_node(self.removed_node)

        self.adjacency = np.matrix(
            [[0, 1, 1, 0, 1],
             [1, 0, 0, 0, 0],
             [1, 0, 0, 0, 0],
             [0, 0, 0, 0, 0],
             [1, 0, 0, 0, 0]], dtype=bool)
        self.minimized_adjacency = np.matrix(
            [[0, 1, 1, 1],
             [1, 0, 0, 0],
             [1, 0, 0, 0],
             [1, 0, 0, 0]], dtype=bool)
        self.expected_nodes = [0, 1, 2, 4]

    def testNetworkX(self):
        star_graph = nx.star_graph(self.number_of_initial_nodes - 1)
        self.assertFalse(
            nx.is_isomorphic(star_graph, self.graph.to_nx()))
        star_graph.remove_node(self.removed_node)
        self.assert_(nx.is_isomorphic(star_graph, self.graph.to_nx()))

    def testNodeToIndex(self):
        for node in xrange(self.number_of_initial_nodes):
            if node < self.removed_node:
                self.assertEqual(node, self.graph.node_to_index(node))
            elif node == self.removed_node:
                self.assertRaises(IndexError, self.graph.node_to_index, node)
            else:
                self.assertEqual(node-1, self.graph.node_to_index(node))

    def testNTI(self):
        NTI = self.graph.NTI

        testing.assert_array_equal(
            [0, 1, 2, 3],
            NTI[:]
        )

        testing.assert_array_equal(
            [0, 1, 2, 3],
            NTI[[0, 1, 2, 3, 4]]
        )

        testing.assert_array_equal(
            [0, 1, 2, 3],
            NTI[[0, 1, 2, 4]]
        )

        testing.assert_array_equal(
            [0, 1, 2],
            NTI[[0, 1, 2]]
        )

    def testITN(self):
        ITN_array = self.graph.ITN
        testing.assert_array_equal(
            self.expected_nodes,
            ITN_array
        )

    def testIndexToNode(self):
        for index, node in zip(xrange(self.graph.number_of_nodes()),
                               self.expected_nodes):
            self.assertEqual(node, self.graph.index_to_node(index))

    @skip('...')
    def testNumpyNotMinimized(self):
        testing.assert_array_equal(
            self.adjacency,
            self.graph.to_numpy(minimize=False))

    @skip('...')
    def testScipyNotMinimized(self):
        testing.assert_array_equal(
            self.adjacency,
            self.graph.to_scipy(minimize=False).todense())

    @skip('...')
    def testScipyMinimized(self):
        (matrix,
         to_matrix_indices,
         from_matrix_indices) = self.graph.to_scipy(minimize=True)
        testing.assert_array_equal(
            self.minimized_adjacency, matrix.todense())
        testing.assert_array_equal(
            [0, 1, 2, 4],
            from_matrix_indices[:],
        )
        testing.assert_array_equal(
            [0, 1, 2, 3],
            to_matrix_indices[:],
        )

    @skip('...')
    def testNumpyMinimized(self):
        (matrix,
         to_matrix_indices,
         from_matrix_indices) = self.graph.to_numpy(minimize=True)
        testing.assert_array_equal(
            [0, 1, 2, 4],
            from_matrix_indices,
        )
        testing.assert_array_equal(
            self.minimized_adjacency,
            matrix.todense())

