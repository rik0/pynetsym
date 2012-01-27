import abc
from unittest import TestCase
from pynetsym import metautil
import networkx as nx

__author__ = 'enrico'


class A(object):
    def foo(self):
        pass

    def bar(self):
        pass

class C(nx.Graph):
    pass

class D(A, C):
    pass

class TestExtract_interface(TestCase):
    def test_extract_all_methods(self):
        @metautil.extract_interface(D)
        class E(object):
            pass
        self.maxDiff = None
        self.assertSequenceEqual(
            dir(D), dir(E))

    def test_methods(self):
        @metautil.extract_interface(D)
        class E(object):
            __metaclass__ = abc.ABCMeta
            pass

