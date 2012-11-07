import unittest
from pynetsym.generation_models import nx_barabasi_albert as barabasi_albert


class TestBA(unittest.TestCase):
    def testRun(self):
        starting_network_size = 100
        steps = 1000
        starting_connections = 20

        # FIXME: we have a bug starting_edges, not starting_connections!
        sim = barabasi_albert.BA()
        sim.run(
                starting_network_size=starting_network_size,
                steps=steps,
                starting_connections=starting_connections)
        with sim.graph.handle as graph:
            self.assertEquals(
                   starting_network_size + steps,
                   graph.number_of_nodes())

