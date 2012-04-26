import unittest

from pynetsym import metautil


class B(object):
    foo = {'x'}


class A(B):
    foo = {'y'}


class TestAccumulateOlderVariants(unittest.TestCase):
    def testA(self):
        self.assertSetEqual({'x', 'y'},
            metautil.gather_from_ancestors(A, 'foo'))

    def testB(self):
        self.assertSetEqual({'x'},
            metautil.gather_from_ancestors(B, 'foo'))

    def testAList(self):
        self.assertSetEqual({'x', 'y'},
            metautil.gather_from_ancestors(A, 'foo'), list)

    def testBList(self):
        self.assertSetEqual({'x'},
            metautil.gather_from_ancestors(B, 'foo'), list)
