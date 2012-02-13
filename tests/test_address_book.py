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

    def test_hint_fails_if_improper_type(self):
        self.assertRaises(
            TypeError,
            self.address_book.create_id_from_hint,
            5.6 )

        self.assertRaises(
            TypeError,
            self.address_book.create_id_from_hint,
            object())

    def test_id_starts_with_string(self):
        str_value = 'foo'
        self.address_book.register(str_value, FakeAgent())
        new_id = self.address_book.create_id_from_hint(str_value)
        self.assert_(new_id.startswith(str_value), "Starts with substring")

    def test_generated_id_is_random_str(self):
        str_value = 'foo'
        self.address_book.register(str_value, FakeAgent())
        new_id = self.address_book.create_id_from_hint(str_value)
        another_id = self.address_book.create_id_from_hint(str_value)
        self.assertNotEqual(new_id, another_id)

    def test_generated_not_random_int(self):
        int_value = 7
        self.address_book.register(int_value, FakeAgent())
        new_id = self.address_book.create_id_from_hint(int_value)
        another_id = self.address_book.create_id_from_hint(int_value)
        self.assertEqual(new_id, another_id)

    def test_generated_key_tries_not_to_increase(self):
        int_value = 1
        self.address_book.register(int_value, FakeAgent())
        new_id = self.address_book.create_id_from_hint(int_value)
        self.assert_(new_id < int_value)
        self.assert_(new_id >= 0)

    def test_generated_key_non_negative(self):
        int_value = 0
        self.address_book.register(int_value, FakeAgent())
        new_id = self.address_book.create_id_from_hint(int_value)
        self.assert_(new_id >= 0)

    def test_generated_key_below_range(self):
        min_key = 3
        keys = set(range(min_key, 7))
        [self.address_book.register(k, FakeAgent()) for k in keys]
        new_id = self.address_book.create_id_from_hint(min_key)
        self.assertEqual(new_id, min_key - 1)

    def test_generated_key_above_range(self):
        min_key = 0
        max_key = 7
        keys = set(range(min_key, max_key))
        [self.address_book.register(k, FakeAgent()) for k in keys]
        new_id = self.address_book.create_id_from_hint(min_key)
        self.assertEqual(new_id, max_key)


    def test_generated_key_in_range(self):
        min_key = 0
        max_key = 7
        keys = set(range(min_key, max_key))
        missing = keys.pop()
        [self.address_book.register(k, FakeAgent()) for k in keys]
        new_id = self.address_book.create_id_from_hint(min_key)
        self.assertEqual(new_id, missing)

