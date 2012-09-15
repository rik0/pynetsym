import unittest
from oldutil import metautil

class TestRootAddressBook(unittest.TestCase):
    
    def setUp(self):
        self.get_root_address_book, \
        self.set_root_address_book = metautil.encapsulate_global('root', {})
        
    def testEmpty(self):
        self.assertRaises(NameError, self.get_root_address_book)
        
    def testSet(self):
        value = object()
        self.set_root_address_book(value)
        self.assertEquals(value, self.get_root_address_book())