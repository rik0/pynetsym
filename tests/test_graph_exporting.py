from numpy import testing, arange
import numpy as np
import paramunittest
from pynetsym.graph import ScipyGraph, NxGraph, DirectedScipyGraph
import networkx as nx


class TGraphExportingBase():
    def setParameters(self, factory, arguments):
        self.factory = factory
        self.arguments = arguments

    def setUp(self):
        self.formats = ['csr', 'csc', 'dok', 'lil', 'coo']
        self.removed_node = 3
        self.number_of_initial_nodes = 5

        self.graph = self.factory(*self.arguments)
        self.graph.add_nodes(self.number_of_initial_nodes)
        for target in xrange(1, self.number_of_initial_nodes):
            self.graph.add_edge(0, target)

        self.graph.remove_node(self.removed_node)
        self.expected_nodes = [0, 1, 2, 4]

    def testNetworkX(self):
        self.assertFalse(
            nx.is_isomorphic(self.star_graph, self.graph.to_nx()))
        self.star_graph.remove_node(self.removed_node)
        self.assert_(nx.is_isomorphic(self.star_graph, self.graph.to_nx()))

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

    def testNumpyNotMinimized(self):
        testing.assert_array_equal(
            self.adjacency,
            self.graph.to_numpy(minimize=False))

    def testScipyNotMinimized(self):
        for format in self.formats:
            testing.assert_array_equal(
                self.adjacency,
                self.graph.to_scipy(sparse_type=format,
                                    minimize=False).tolil().todense())

    def testScipyMinimized(self):
        for format in self.formats:
            (matrix,
             node_to_index,
             index_to_node) = self.graph.to_scipy(sparse_type=format, minimize=True)
            testing.assert_array_equal(
                node_to_index[index_to_node],
                arange(matrix.shape[0]))
            testing.assert_array_equal(
                self.minimized_adjacency,
                matrix.tolil().todense())

    def testNumpyMinimized(self):
        (matrix,
         node_to_index,
         index_to_node) = self.graph.to_numpy(minimize=True)
        testing.assert_array_equal(
            node_to_index[index_to_node],
            arange(matrix.shape[0]))
        testing.assert_array_equal(
            self.minimized_adjacency,
            matrix)

@paramunittest.parametrized(
    (ScipyGraph, (12, )),
    (NxGraph, ())
)
class TestGraphExporting(TGraphExportingBase, paramunittest.ParametrizedTestCase):
    def setUp(self):
        TGraphExportingBase.setUp(self)
        self.star_graph = nx.star_graph(self.number_of_initial_nodes - 1)
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

@paramunittest.parametrized(
    (DirectedScipyGraph, (12, )),
    (NxGraph, (nx.DiGraph, ))
)
class TestGraphExportingDirected(TGraphExportingBase, paramunittest.ParametrizedTestCase):
    def setUp(self):
        TGraphExportingBase.setUp(self)
        self.star_graph = nx.star_graph(
            self.number_of_initial_nodes - 1)
        self.star_graph = nx.DiGraph(data=self.star_graph.edges())
        self.adjacency = np.matrix(
            [[0, 1, 1, 0, 1],
             [0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0]], dtype=bool)
        self.minimized_adjacency = np.matrix(
            [[0, 1, 1, 1],
             [0, 0, 0, 0],
             [0, 0, 0, 0],
             [0, 0, 0, 0]], dtype=bool)