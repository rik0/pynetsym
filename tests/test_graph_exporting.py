import unittest
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

    def testNetworkX(self):
        star_graph = nx.star_graph(self.number_of_initial_nodes - 1)
        self.assertFalse(
            nx.is_isomorphic(star_graph, self.graph.to_nx()))
        star_graph.remove_node(self.removed_node)
        self.assert_(nx.is_isomorphic(star_graph, self.graph.to_nx()))

    def testNumpyNotMinimized(self):
        testing.assert_array_equal(
            self.adjacency,
            self.graph.to_numpy(minimize=False))

    def testScipyNotMinimized(self):
        testing.assert_array_equal(
            self.adjacency,
            self.graph.to_scipy(minimize=False).todense())

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

