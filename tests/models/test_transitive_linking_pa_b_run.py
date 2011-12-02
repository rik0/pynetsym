import unittest

import networkx as nx

from pynetsym import generation
from pynetsym.models import transitive_linking_pa_b


class TestTransitiveLinkingRun(unittest.TestCase):
    def setUp(self):
        self.graph = nx.Graph()

    def test(self):
        generation.generate(self.graph, transitive_linking_pa_b, 1000,
                            network_size=100, death_probability=0.01)