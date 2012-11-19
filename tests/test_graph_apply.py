from unittest import TestCase
from pynetsym.graph import ScipyGraph, NxGraph

import networkx as nx


class TestSkeleton(object):
    def setUp(self):
        self.number_of_nodes = 5
        self.graph = self.makeGraph()
        self.graph.add_nodes(self.number_of_nodes)
        for target in xrange(1, self.number_of_nodes):
            self.graph.add_edge(0, target)

        self.expected_nodes = range(self.number_of_nodes)


class TestGraphApplyNXGraph(TestSkeleton, TestCase):
    def makeGraph(self):
        return NxGraph(nx.Graph())

    def testApply(self):
        self.assertEqual(
            len(self.expected_nodes),
            self.graph.apply(nx.number_of_nodes))

        self.assertEqual(
            len(self.expected_nodes)-1,
            self.graph.apply(nx.number_of_edges))

    def testContext(self):
        with self.graph.handle as handle:
            self.assertEqual(
                len(self.expected_nodes),
                handle.number_of_nodes())
            self.assertEqual(
                len(self.expected_nodes)-1,
                handle.number_of_edges())

    def testContextCopy(self):
        with self.graph.handle_copy as handle:
            self.assertEqual(
                len(self.expected_nodes),
                handle.number_of_nodes())
            self.assertEqual(
                len(self.expected_nodes)-1,
                handle.number_of_edges())

            handle.add_node(self.number_of_nodes)
            self.assertEqual(
                len(self.expected_nodes) + 1,
                handle.number_of_nodes())

        self.assertEqual(
            len(self.expected_nodes),
            self.graph.apply(nx.number_of_nodes))

class TestGraphApplyScipy(TestSkeleton, TestCase):

    def makeGraph(self):
        return ScipyGraph(12)

    def testApply(self):
        self.assertEqual(
            len(self.expected_nodes)-1,
            self.graph.apply(lambda G: G.getnnz() / 2))

    def testContext(self):
        with self.graph.handle as handle:
            self.assertEqual(
                len(self.expected_nodes) - 1,
                handle.getnnz()/2)

    def testContextCopy(self):
        with self.graph.handle_copy as handle:
            self.assertEqual(
                len(self.expected_nodes) - 1,
                handle.getnnz()/2)
            handle[2,3] = handle[3,2] = True
            self.assertEqual(
                len(self.expected_nodes),
                handle.getnnz()/2)
        self.assertEqual(
            len(self.expected_nodes)-1,
            self.graph.apply(lambda G: G.getnnz() / 2))