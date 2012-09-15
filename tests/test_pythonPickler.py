from unittest import TestCase
import pynetsym.agent_db

import itertools as it

class TestPythonPickler(TestCase):
    currentPickler = pynetsym.agent_db.PythonPickler

    def setUp(self):
        self.pickler = self.currentPickler()
        self.objects = [1, 4, 'hi', dict(foo='bar'), [3, 4, 2],
                        set((2, )), frozenset((3, 5))]

    def testSingleton(self):
        # we hate singletons... but that is an interface over a module
        self.assertIs(self.pickler, self.currentPickler())

    def test_roundtrip(self):
        ld = self.pickler.loads
        dm = self.pickler.dumps
        self.assertListEqual(self.objects, [ld(dm(obj)) for obj in
                                               self.objects])

class TestJSONPickler(TestPythonPickler):
    currentPickler = pynetsym.agent_db.JSONPickle

    def setUp(self):
        super(TestJSONPickler, self).setUp()
        # jsonpickle does not deal with frozensets correctly
        self.objects = it.ifilterfalse(
            lambda o: isinstance(o, frozenset), self.objects)
        self.objects = list(self.objects)

