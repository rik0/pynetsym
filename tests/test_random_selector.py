import networkx as nx

from unittest import TestCase
from pynetsym.graph.nx_impl import NxRandomSelector

class TestRandomSelector(TestCase):
    def setUp(self):
        self.nodes = 10
        self.graph = nx.star_graph(self.nodes-1)
        self.random_selector = NxRandomSelector(graph=self.graph)

    def testAddNode(self):
        self.random_selector.preferential_attachment()
        self.random_selector.add_node(self.nodes)

    def testAddNodeUnprepared(self):
        self.random_selector.add_node(self.nodes)

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
                self.assertEqual(old_edges - node_degree * 2,
                                 len(self.random_selector.repeated_nodes))

    def testRemoveNodeUnprepared(self):
        self.random_selector.remove_node(0)

    def testRemoveEdge(self):
        self.random_selector.preferential_attachment()
        old_edges = len(self.random_selector.repeated_nodes)
        self.graph.remove_edge(0, 2)
        self.random_selector.remove_edge(0, 2)
        self.random_selector.preferential_attachment()
        self.assertEqual(old_edges-2,
                         len(self.random_selector.repeated_nodes))

    def testRemoveEdgeUnprepared(self):
        self.random_selector.remove_edge(0, 2)

    def testRemoveEdge2(self):
        self.random_selector.preferential_attachment()
        old_edges = len(self.random_selector.repeated_nodes)
        self.graph.remove_edge(0, 9)
        self.random_selector.remove_edge(0, 9)
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
        self.random_selector.remove_edge(5, 9)
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
        self.random_selector.remove_edge(5, 4)
        self.random_selector.preferential_attachment()
        self.assertEqual(old_edges-2,
                         len(self.random_selector.repeated_nodes))

    def testRemoveEdgeUnprepared4(self):
        self.random_selector.remove_edge(5, 4)

    def testAddEdge(self):
        self.random_selector.preferential_attachment()
        old_edges = len(self.random_selector.repeated_nodes)
        self.graph.add_edge(5, 4)
        self.random_selector.add_edge(5, 4)
        self.random_selector.preferential_attachment()
        self.assertEqual(old_edges+2,
                         len(self.random_selector.repeated_nodes))

    def testAddEdgeUnprepared4(self):
        self.random_selector.add_edge(5, 4)