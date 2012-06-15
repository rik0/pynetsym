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

    def test_unregister_ns(self):
        self.address_book.unregister_namespace(self.namespace_name)
        self.assertRaises(addressing.AddressingError,
                          self.address_book.resolve, self.namespace_name, 'present')

    def test_unregister_agent(self):
        self.address_book.unregister(self.namespace_name, 'present')
        self.assertRaises(addressing.AddressingError,
                          self.address_book.resolve, self.namespace_name, 'present')

    def test_unregister_fake_namespace(self):
        self.assertRaises(addressing.AddressingError,
                          self.address_book.unregister_namespace,
                          'fake_namespace')

    def test_composite_list(self):
        another_address_book = addressing.FlatAddressBook()
        another_object = object()
        another_address_book.register('another_object', another_object)

        self.address_book.register_namespace('another_namespace', another_address_book)

        complete_list = self.address_book.list()

        for identifier in self.address_book.list_iter():
            if identifier in map(lambda x: ('another_namespace', x), another_address_book.list()):
                complete_list.remove(identifier)
            if identifier in map(lambda x: (self.namespace_name, x), self.flat_address_book.list()):
               complete_list.remove(identifier)

        self.assertEqual([], complete_list)

