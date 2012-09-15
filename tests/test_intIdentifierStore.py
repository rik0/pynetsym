from unittest import TestCase
from pynetsym import util
from pynetsym.identifiers_manager import IntIdentifierStore


class TestIntIdentifierStore(TestCase):
    def setUp(self):
        self.store = IntIdentifierStore()

    def perform_actions(self, action_list):
        for action_item in action_list:
            action, params = action_item[0], action_item[1:]
            getattr(self.store, action)(*params)

    def testPeek(self):
        self.assertEqual(0, self.store.peek())

    def testPop(self):
        self.assertEqual(0, self.store.pop())
        self.assertEqual(1, self.store.peek())
