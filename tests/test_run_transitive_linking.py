import unittest
from pynetsym.generation_models import transitive_linking
from pynetsym.generation_models import transitive_linking_b
from pynetsym.generation_models import transitive_linking_igraph


class TestTL(unittest.TestCase):
    def setUp(self):
        self.args = "-n 100 --death-probability 0.01"

    def testTL(self):
        sim = transitive_linking.TL()
        sim.run(args=self.args)

    def testTLB(self):
        sim = transitive_linking_b.TL()
        sim.run(args=self.args)

    def testTL_igraph(self):
        sim = transitive_linking_igraph.TL()
        sim.run(args=self.args)

    def testTL_pa(self):
        self.args += ' --preferential-attachment'
        sim = transitive_linking.TL()
        sim.run(args=self.args)

    def testTLB_pa(self):
        self.args += ' --preferential-attachment'
        sim = transitive_linking_b.TL()
        sim.run(args=self.args)

    def testTL_igraph_pa(self):
        self.args += ' --preferential-attachment'
        sim = transitive_linking_igraph.TL()
        sim.run(args=self.args)
