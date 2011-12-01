import unittest
from pynetsym import core

class FakeAgent(object):
    def __init__(self, identifier=0):
        self.id = identifier

class TestAddressBook(unittest.TestCase):
    def setUp(self):
        self.address_book = core.AddressBook()

    @unittest.expectedFailure
    def testEmpty(self):
        self.address_book.resolve('not_existent')

    def fillWithValues(self, **kwargs):
        for k, v in kwargs.iteritems():
            self.address_book.register(k, v)

    def testNotEmpty(self):
        agent = FakeAgent()
        self.fillWithValues(a=agent)
        self.assertEqual(
            agent,
            self.address_book.resolve('a')
        )

    @unittest.expectedFailure
    def testReRegister(self):
        agent_a = FakeAgent()
        agent_b = FakeAgent()
        self.fillWithValues(a=agent_a)
        self.address_book.register('a', agent_b)

    def testSelfReRegister(self):
        agent_a = FakeAgent()
        self.fillWithValues(a=agent_a)
        self.address_book.register('a', agent_a)

