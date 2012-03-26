import unittest
from pynetsym.generation_models import transitive_linking
from pynetsym.generation_models import transitive_linking_b
from pynetsym.generation_models import transitive_linking_igraph

class TestTL(unittest.TestCase):
    def testTL(self):
        self.sim = transitive_linking.TL()
        self.sim.run()
    def testTLB(self):
        self.sim = transitive_linking_b.TL()
        self.sim.run()
    def testTL_igraph(self):
        self.sim = transitive_linking_igraph.TL()
        self.sim.run()
    def testTL_pa(self):
        self.sim = transitive_linking.TL()
        self.sim.run(args=["--preferential-attachment"])
    def testTLB_pa(self):
        self.sim = transitive_linking_b.TL()
        self.sim.run(args=["--preferential-attachment"])
    def testTL_igraph_pa(self):
        self.sim = transitive_linking_igraph.TL()
        self.sim.run(args=["--preferential-attachment"])
