from unittest import TestCase
from paramunittest import parametrized, ParametrizedTestCase
from pynetsym.graph._util import DefaultIndexMap


class TestDefaultIndexMap(TestCase):
    def testEmpty(self):
        default_index_map = DefaultIndexMap()
        for item in [1, 'a', 'foo', 5.6]:
            self.assertEqual(item, default_index_map[item])

    def testWithValues(self):
        default_index_map = DefaultIndexMap(a=1, b=2)
        self.assertEqual(1, default_index_map['a'])
        self.assertEqual(2, default_index_map['b'])
        self.assertEqual(2, default_index_map[2])

    def testWithValues2(self):
        default_index_map = DefaultIndexMap({1: 2, 2: 3})
        self.assertEqual(2, default_index_map[1])
        self.assertEqual(3, default_index_map[2])
        self.assertEqual(3, default_index_map[3])

    def testWithValues3(self):
        default_index_map = DefaultIndexMap({1: 2, 2: 3}, a=1)
        self.assertEqual(1, default_index_map['a'])
        self.assertEqual(2, default_index_map[1])
        self.assertEqual(3, default_index_map[2])
        self.assertEqual(3, default_index_map[3])

    def testWithValues3(self):
        default_index_map = DefaultIndexMap(default_function=lambda x: x * 2,
                                            dictionary={1: 2, 2: 3}, a=1)
        self.assertEqual(1, default_index_map['a'])
        self.assertEqual(2, default_index_map[1])
        self.assertEqual(3, default_index_map[2])
        self.assertEqual(6, default_index_map[3])
        self.assertEqual('bb', default_index_map['b'])


@parametrized(
    *[(tuple(el), ) for el in
      [[1, 2, 3],
       [1, 3],
       [7, 8, 9],
       range(10),
       range(3, 30, 5),
       list('foobar')]]
)
class TestMultipleIndexes(ParametrizedTestCase):
    def setParameters(self, lst):
        self.lst = lst

    def setUp(self):
        self.index_map = DefaultIndexMap()

    def testSequence(self):
        self.assertListEqual(
            self.lst, self.index_map[self.lst])
