import unittest
from pynetsym import core

class FakeAgent(object):
    def __init__(self, identifier=0):
        self.id = identifier

class TestAddressBook(unittest.TestCase):
    def setUp(self):
        self.address_book = core.AddressBook()

    def fillWithValues(self, **kwargs):
        for k, v in kwargs.iteritems():
            self.address_book.register(k, v)

    def testEmpty(self):
        self.assertRaises(
            core.AddressingError,
            self.address_book.resolve, 'not_existent')

    def testNotEmpty(self):
        agent = FakeAgent()
        self.fillWithValues(a=agent)
        self.assertEqual(
            agent,
            self.address_book.resolve('a')
        )

    def testReRegister(self):
        agent_a = FakeAgent()
        agent_b = FakeAgent()
        self.fillWithValues(a=agent_a)
        self.assertRaises(
            core.AddressingError,
            self.address_book.register, 'a', agent_b)

    def testSelfReRegister(self):
        agent_a = FakeAgent()
        self.fillWithValues(a=agent_a)
        self.address_book.register('a', agent_a)

    def test_new_id_is_good_hint_str(self):
        string_value = 'new_name'
        self.assertEqual(
            string_value,
            self.address_book.create_id_from_hint(string_value))

    def test_new_id_is_good_hint_int(self):
        int_value = 42
        self.assertEqual(
            int_value,
            self.address_book.create_id_from_hint(int_value))


