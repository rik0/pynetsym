import unittest
from pynetsym import addressing


class TestFlatAddressBook(unittest.TestCase):
    def setUp(self):
        self.address_book = addressing.FlatAddressBook()

    def fillWithValues(self, **kwargs):
        for k, v in kwargs.iteritems():
            self.address_book.register(k, v)

    def testEmpty(self):
        self.assertRaises(
            addressing.AddressingError,
            self.address_book.resolve, 'not_existent')

    def testNotEmpty(self):
        agent = object()
        self.fillWithValues(a=agent)
        self.assertEqual(
            agent,
            self.address_book.resolve('a'))

    def testReRegister(self):
        agent_a = object()
        agent_b = object()
        self.fillWithValues(a=agent_a)
        self.assertRaises(
            addressing.AddressingError,
            self.address_book.register, 'a', agent_b)

    def testSelfReRegister(self):
        agent_a = object()
        self.fillWithValues(a=agent_a)
        self.address_book.register('a', agent_a)

class TestNamespacedAddressBook(unittest.TestCase):
    def setUp(self):
        self.present_object = object()
        self.flat_address_book = addressing.FlatAddressBook()
        self.flat_address_book.register('present', self.present_object)
        self.address_book = addressing.NamespacedAddressBook()
        self.namespace_name = 'ns'
        self.address_book.register_namespace(self.namespace_name, self.flat_address_book)

    def test_existing(self):
        self.assertEqual(self.present_object,
                         self.address_book.resolve(self.namespace_name, 'present'))

    def test_non_existing_agent(self):
        self.assertRaises(addressing.AddressingError,
                          self.address_book.resolve, self.namespace_name, 'absent')

    def test_non_existing_namespace(self):
        self.assertRaises(addressing.AddressingError,
                          self.address_book.resolve, 'invalid_namespace', 'present')
