import unittest
from pynetsym.generation_models import bpa


class TestBPA(unittest.TestCase):
    def testRun(self):
        network_size = 100
        gamma = 0.01
        probability = '1/3:1/3:1/3'
        edges = 4

        sim = bpa.BPA()
        sim.run(network_size=network_size,
                gamma=gamma,
                probability=probability,
                edges=edges)
