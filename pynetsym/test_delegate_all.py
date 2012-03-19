from unittest import TestCase
import pynetsym.metautil

__author__ = 'enrico'

class BaseClass(object):
    ANSWER = 42

    def __init__(self, val):
        self.val = val

    def a_method(self):
        return self.ANSWER

    def a_method_with_parameter(self, par):
        return par

    def a_setter(self, val):
        self.val = val

    def a_getter(self):
        return self.val

    @property
    def a_read_only_property(self):
        return self.ANSWER

@pynetsym.metautil.delegate_all(BaseClass)
class StandardDelegator(object):
    def __init__(self, delegate):
        self.delegate = delegate


class TestDelegate_all(TestCase):
    def setUp(self):
        self.base = BaseClass(10)
        self.standard_delegator = StandardDelegator(self.base)

    def testAMethod(self):
        self.assertEqual(self.base.a_method(),
            self.standard_delegator.a_method())

    def testAMethodWithParameter(self):
        value = 42
        self.assertEquals(
            self.base.a_method_with_parameter(value),
            self.standard_delegator.a_method_with_parameter(value))

    def testASetter(self):
        value = 42
        self.standard_delegator.a_setter(42)
        self.assertEqual(
            value, self.standard_delegator.a_getter())
