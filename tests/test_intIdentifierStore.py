from unittest import TestCase
from paramunittest import parametrized
from pynetsym.identifiers_manager import IntIdentifierStore


class TestBasicIntIdentifierStore(TestCase):
    def setUp(self):
        self.store = IntIdentifierStore()

    def testPeek(self):
        self.assertEqual(0, self.store.peek())

    def testPop(self):
        self.assertEqual(0, self.store.pop())
        self.assertEqual(1, self.store.peek())


@parametrized(
    (0, ),
    (1, 'pop'),
    (1, 'pop', ('unmark', 1)),
    (0, 'pop', ('unmark', 0)),
    (3, 'pop', 'pop', 'pop'),
    (2, 'pop', 'pop', 'pop', ('unmark', 2)),
    (1, 'pop', 'pop', 'pop', ('unmark', 1)),
    (0, 'pop', 'pop', 'pop', ('unmark', 0)),
    (3, 'pop', 'pop', 'pop', ('unmark', 2), 'pop'),
    (2, 'pop', 'pop', 'pop', ('unmark', 1), ('unmark', 2), 'pop'),
    (2, 'pop', 'pop', 'pop', ('unmark', 2), ('unmark', 1), 'pop'),
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