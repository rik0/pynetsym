import unittest
from pynetsym.generation_models import watts_strogatz


class TestWS(unittest.TestCase):
    def testRun(self):
        rewiring_probability = 0.1
        lattice_connections = 2
        starting_network_size = 100

        sim = watts_strogatz.WS()
        sim.run(
            rewiring_probability=rewiring_probability,
            lattice_connections=lattice_connections,
            starting_network_size=starting_network_size)

        graph = sim.graph.handle
        self.assertEqual(
                starting_network_size,
                graph.number_of_nodes())
        self.assertEqual(
                starting_network_size * lattice_connections,
                graph.number_of_edges())
