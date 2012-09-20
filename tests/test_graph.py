import unittest
import paramunittest

from pynetsym.graph import NxGraph, ScipyGraph


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