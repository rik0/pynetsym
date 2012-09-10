import unittest

from unittest import skipUnless

try:
    from pynetsym.generation_models import transitive_linking
    from pynetsym.generation_models import transitive_linking_b
    has_nx = True
except ImportError:
    has_nx = False

try:
    from pynetsym.generation_models import transitive_linking_igraph
    has_igraph = True
except ImportError:
    has_igraph = False


class TestTL(unittest.TestCase):
    def setUp(self):
        self.args = "-n 100 --death-probability 0.01"

    @skipUnless(has_nx, "NX could not be imported")
    def testTL(self):
        sim = transitive_linking.TL()
        sim.run(args=self.args)

    @skipUnless(has_nx, "NX could not be imported")
    def testTLB(self):
        sim = transitive_linking_b.TL()
        sim.run(args=self.args)

    @skipUnless(has_igraph, "Igraph could not be imported")
    def testTL_igraph(self):
        sim = transitive_linking_igraph.TL()
        sim.run(args=self.args)

    @skipUnless(has_nx, "NX could not be imported")
    def testTL_pa(self):
        self.args += ' --preferential-attachment'
        sim = transitive_linking.TL()
        sim.run(args=self.args)

    @skipUnless(has_nx, "NX could not be imported")
    def testTLB_pa(self):
        self.args += ' --preferential-attachment'
        sim = transitive_linking_b.TL()
        sim.run(args=self.args)

    @skipUnless(has_igraph, "Igraph could not be imported")
    def testTL_igraph_pa(self):
        self.args += ' --preferential-attachment'
        sim = transitive_linking_igraph.TL()
        sim.run(args=self.args)
