from scipy import sparse
import networkx as nx

from unittest import TestCase
from pynetsym.graph.nx_impl import  NxGraph
from pynetsym.graph.scipy_impl import  ScipyGraph, DirectedScipyGraph

class AbstractTestRandomSelector(object):
    def testAddNode(self):
        self.random_selector.preferential_attachment()
        old_edges = len(self.random_selector.repeated_nodes)
        self.graph.add_node()
        self.random_selector.preferential_attachment()
        self.assertEqual(old_edges+1,
                         len(self.random_selector.repeated_nodes))

    def testAddNodeUnprepared(self):
        self.graph.add_node()

    def testRemoveNode(self):
        self.random_selector.preferential_attachment()
        for node in reversed(xrange(self.nodes)):
            old_edges = len(self.random_selector.repeated_nodes)
            node_degree = self.graph.degree(node)
            self.graph.remove_node(node)
            self.random_selector.remove_node(node)
            try:
                self.random_selector.preferential_attachment()
            except IndexError:
                pass
            else:
                self.assertEqual(old_edges - node_degree * 2 - 1,
                                 len(self.random_selector.repeated_nodes))

    def testRemoveNodeUnprepared(self):
        self.random_selector.remove_node(0)

    def testRemoveEdge(self):
        self.random_selector.preferential_attachment()
        old_edges = len(self.random_selector.repeated_nodes)
        self.graph.remove_edge(0, 2)
        self.random_selector.preferential_attachment()
        self.assertEqual(old_edges-2,
                         len(self.random_selector.repeated_nodes))

    def testRemoveEdgeUnprepared(self):
        self.random_selector.remove_edge(0, 2)

    def testRemoveEdge2(self):
        self.random_selector.preferential_attachment()
        old_edges = len(self.random_selector.repeated_nodes)
        self.graph.remove_edge(0, 9)
        self.random_selector.preferential_attachment()
        self.assertEqual(old_edges-2,
                         len(self.random_selector.repeated_nodes))

    def testRemoveEdgeUnprepared2(self):
        self.random_selector.remove_edge(0, 9)

    def testRemoveEdge3(self):
        self.graph.add_edge(5, 9)
        self.random_selector.preferential_attachment()
        old_edges = len(self.random_selector.repeated_nodes)
        self.graph.remove_edge(5, 9)
        self.random_selector.preferential_attachment()
        self.assertEqual(old_edges-2,
                         len(self.random_selector.repeated_nodes))

    def testRemoveEdgeUnprepared3(self):
        self.random_selector.remove_edge(5, 9)

    def testRemoveEdge4(self):
        self.graph.add_edge(5, 4)
        self.random_selector.preferential_attachment()
        old_edges = len(self.random_selector.repeated_nodes)
        self.graph.remove_edge(5, 4)
        self.random_selector.preferential_attachment()
        self.assertEqual(old_edges-2,
                         len(self.random_selector.repeated_nodes))

    def testRemoveEdgeUnprepared4(self):
        self.random_selector.remove_edge(5, 4)

    def testAddEdge(self):
        self.random_selector.preferential_attachment()
        old_edges = len(self.random_selector.repeated_nodes)
        self.graph.add_edge(5, 4)
        self.random_selector.preferential_attachment()
        self.assertEqual(old_edges+2,
                         len(self.random_selector.repeated_nodes))

    def testAddEdgeUnprepared4(self):
        self.random_selector.add_edge(5, 4)

class TestNxRandomSelector(AbstractTestRandomSelector, TestCase):
    def setUp(self):
        self.nodes = 10
        star = nx.star_graph(self.nodes-1)
        self.graph = NxGraph(data=star.edges())
        self.random_selector = self.graph.random_selector

class TestScipyRandomSelector(AbstractTestRandomSelector, TestCase):
    def setUp(self):
        self.nodes = 10
        matrix = sparse.lil_matrix((self.nodes,
                                    self.nodes), dtype=bool)
        matrix[0, :] = matrix[:, 0] = 1
        matrix[0,0]= 0
        self.graph = ScipyGraph(matrix=matrix)

        self.random_selector = self.graph.random_selector

class TestDirectedScipyRandomSelector(AbstractTestRandomSelector, TestCase):
    def setUp(self):
        self.nodes = 10
        matrix = sparse.lil_matrix((self.nodes,
                                    self.nodes), dtype=bool)
        matrix[0, :] = matrix[:, 0] = 1
        matrix[0,0]= 0
        self.graph = DirectedScipyGraph(matrix=matrix)

        self.random_selector = self.graph.random_selector