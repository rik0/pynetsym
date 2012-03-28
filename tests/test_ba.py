import unittest
from pynetsym.generation_models import barabasi_albert

class TestBA(unittest.TestCase):
    def testRun(self):
        network_size = 100
        steps = 1000
        starting_connections = 20

        sim = barabasi_albert.BA()
        sim.run(
                network_size=network_size,
                steps=steps,
                starting_connections=starting_connections)
        graph = sim.graph.handle

        self.assertEquals(
               network_size+steps,
               graph.number_of_nodes())

