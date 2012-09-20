from unittest import TestCase
from paramunittest import parametrized
from pynetsym.identifiers_manager import IntIdentifierStore


class TestBasicIntIdentifierStore(TestCase):
    def setUp(self):
        self.store = IntIdentifierStore()

    def testPeek(self):
        self.assertEqual(0, self.store.peek())

    def testget(self):
        self.assertEqual(0, self.store.get())
        self.assertEqual(1, self.store.peek())

    def testDoubleFreeFIFO(self):
        self.store.get()
        self.assertEqual(1, self.store.peek())
        self.store.get()
        self.assertEqual(2, self.store.peek())
        self.store.free(0)
        self.assertEqual(0, self.store.peek())
        self.store.free(1)
        self.assertEqual(0, self.store.peek())

    def testDoubleFreeLIFO(self):
        self.store.get()
        self.assertEqual(1, self.store.peek())
        self.store.get()
        self.assertEqual(2, self.store.peek())
        self.store.free(1)
        self.assertEqual(1, self.store.peek())
        self.store.free(0)
        self.assertEqual(0, self.store.peek())

@parametrized(
    (0, ),
    (1, 'get'),
    (1, 'get', ('free', 1)),
    (0, 'get', ('free', 0)),
    (3, 'get', 'get', 'get'),
    (2, 'get', 'get', 'get', ('free', 2)),
    (1, 'get', 'get', 'get', ('free', 1)),
    (0, 'get', 'get', 'get', ('free', 0)),
    (3, 'get', 'get', 'get', ('free', 2), 'get'),
    (2, 'get', 'get', 'get', ('free', 1), ('free', 2), 'get'),
    (2, 'get', 'get', 'get', ('free', 2), ('free', 1), 'get'),
)
class TestPeek(TestCase):
    def setUp(self):
        self.store = IntIdentifierStore()

    def setParameters(self, result, *actions):
        self.result = result
        self.actions = actions

    def perform_actions(self, action_list):
        for action_item in action_list:
            if isinstance(action_item, basestring):
                action, params = action_item, tuple()
            else:
                action, params = action_item[0], action_item[1:]
            getattr(self.store, action)(*params)

    def test(self):
        self.perform_actions(self.actions)
        self.assertEquals(self.result, self.store.peek())