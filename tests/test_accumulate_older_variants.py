import unittest
import sys

from pynetsym import metautil

class B(object):
    foo = {'x'}

class A(B):
    foo = {'y'}

class TestAccumulateOlderVariants(unittest.TestCase):
    def testA(self):
        self.assertSetEqual({'x', 'y'},
            metautil.accumulate_older_variants(A, 'foo'))

    def testB(self):
        self.assertSetEqual({'x'},
            metautil.accumulate_older_variants(B, 'foo'))

    def testAiList(self):
        self.assertSetEqual({'x', 'y'},
            metautil.accumulate_older_variants(A, 'foo'), list)

    def testBList(self):
        self.assertSetEqual({'x'},
            metautil.accumulate_older_variants(B, 'foo'), list)
