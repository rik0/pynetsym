from unittest import TestCase
from numpy import arange
from paramunittest import parametrized, ParametrizedTestCase
from pynetsym.graph._util import DefaultIndexMap


class TestDefaultIndexMap(TestCase):
    def testEmpty(self):
        default_index_map = DefaultIndexMap()
        for item in range(3):
            self.assertEqual(item, default_index_map[item])

    def testInvalidKeys(self):
        default_index_map = DefaultIndexMap()
        self.assertRaises(TypeError, default_index_map.__getitem__, 'a')
        self.assertRaises(TypeError, default_index_map.__getitem__, 'foo')
        self.assertRaises(TypeError, default_index_map.__getitem__, 5.5)

    def testInvalidKeyInit(self):
        self.assertRaises(TypeError, DefaultIndexMap, {'foo': 2, 2: 3})

    def testWithValues(self):
        default_index_map = DefaultIndexMap({1: 2, 2: 3})
        self.assertEqual(2, default_index_map[1])
        self.assertEqual(3, default_index_map[2])
        self.assertEqual(3, default_index_map[3])

    def testWithNonDefaultFunc(self):
        default_index_map = DefaultIndexMap(default_function=lambda x: x * 2,
                                            dictionary={1: 2, 2: 3})
        self.assertEqual(2, default_index_map[1])
        self.assertEqual(3, default_index_map[2])
        self.assertEqual(6, default_index_map[3])


@parametrized(
    *[(tuple(el), ) for el in
      [[1, 2, 3],
       [1, 3],
       [7, 8, 9],
       range(10),
       range(3, 30, 5)]]
)
class TestSequence(ParametrizedTestCase):
    def setParameters(self, lst):
        self.lst = lst

    def setUp(self):
        self.index_map = DefaultIndexMap()

    def testSequence(self):
        self.assertSequenceEqual(
            self.lst, self.index_map[self.lst])


@parametrized(
    *[(tuple(el), ) for el in
      [[1, 2, 3],
       [1, 3],
       [7, 8, 9],
       range(10),
       range(3, 30, 5)]]
)
class TestSequenceWithMap(ParametrizedTestCase):
    def setParameters(self, lst):
        self.lst = lst

    def setUp(self):
        original_map = dict(zip(arange(5), -arange(5)))
        self.mapped_lst = [-el if 0 <= el < 5 else el for el in self.lst]
        self.index_map = DefaultIndexMap(original_map)

    def testSequence(self):
        self.assertSequenceEqual(
            self.mapped_lst, self.index_map[self.lst])


@parametrized(
    (0, 3, 1),
    (0, 3, 2),
    (0, 3, -1),
    (0, 3, -2),
    (3, 0, -1),
    (3, 0, -2),
    (-10, 10, 1),
    (10, -10, -2)
)
class TestSlices(ParametrizedTestCase):
    def setParameters(self, start, stop, stride):
        self.start = start
        self.stop = stop
        self.stride = stride

    def setUp(self):
        original_map = dict(zip(arange(5), -arange(5)))
        self.index_map = DefaultIndexMap(original_map)

    def testSliceFull(self):
        mapped_lst = [-el if 0 <= el < 5 else el
                      for el in range(self.start, self.stop, self.stride)]

        self.assertSequenceEqual(
            mapped_lst, self.index_map[self.start:self.stop:self.stride])

    def testSliceNoStride(self):
        mapped_lst = [-el if 0 <= el < 5 else el
                      for el in range(self.start, self.stop, 1)]

        self.assertSequenceEqual(
            mapped_lst, self.index_map[self.start:self.stop])