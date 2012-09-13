import unittest
import paramunittest

from pynetsym.generation_models import watts_strogatz
import networkx as nx

@paramunittest.parametrized(
    (0.1, 2, 100),
    (0.1, 2, 1000),
    (0.5, 2, 100),
    (0.5, 2, 1000),
)
class TestWS(unittest.TestCase):
    def setUp(self):
        self.comparison_graph = nx.watts_strogatz_graph(
            self.starting_network_size,
            self.lattice_connections * 2,
            self.rewiring_probability)

    def setParameters(self, rewiring_probability, lattice_connections,
            starting_network_size):
        self.rewiring_probability = rewiring_probability
        self.lattice_connections = lattice_connections
        self.starting_network_size = starting_network_size

    def testRun(self):
        sim = watts_strogatz.WS()
        sim.run(
            steps=self.starting_network_size,
            rewiring_probability=self.rewiring_probability,
            lattice_connections=self.lattice_connections,
            starting_network_size=self.starting_network_size)

        graph = sim.graph.handle
        self.assertEqual(
            self.comparison_graph.number_of_nodes(),
            graph.number_of_nodes())
        self.assertEqual(
            self.comparison_graph.number_of_edges(),
            graph.number_of_edges())

        if False:
            self.assertAlmostEqual(
                nx.diameter(self.comparison_graph),
                nx.diameter(graph),
                delta=1.
            )
            self.assertAlmostEqual(
                nx.average_shortest_path_length(self.comparison_graph),
                nx.average_shortest_path_length(graph),
                delta=1.
            )