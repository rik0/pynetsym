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
        self.delegator = StandardDelegator(self.base)

    def testAMethod(self):
        self.assertEqual(self.base.a_method(),
            self.delegator.a_method())

    def testAMethodWithParameter(self):
        value = 42
        self.assertEquals(
            self.base.a_method_with_parameter(value),
            self.delegator.a_method_with_parameter(value))

    def testASetter(self):
        value = 42
        self.delegator.a_setter(42)
        self.assertEqual(
            value, self.delegator.a_getter())

    def testProperty(self):
        self.assertEqual(
            BaseClass.ANSWER, self.delegator.a_read_only_property)

    def testPropertyReadOnly(self):
        self.assertRaises(
            AttributeError,
            setattr, self.delegator, 'a_read_only_property', 10)

class TestDelegate_all_To_Delegate_Subclass(TestDelegate_all):
    def setUp(self):
        class Subclass(BaseClass):
            def __init__(self, val):
                super(Subclass, self).__init__(val)

        @pynetsym.metautil.delegate_all(Subclass)
        class SubclassDelegator(object):
            def __init__(self, delegate):
                self.delegate = delegate

        self.base = Subclass(10)
        self.delegator = SubclassDelegator(self.base)

class TestDelegate_all_With_Delegator_Subclass(TestDelegate_all):
    def setUp(self):

        class SubclassDelegator(StandardDelegator):
            def __init__(self, delegate):
                super(SubclassDelegator, self).__init__(delegate)

        self.base = BaseClass(10)
        self.delegator = SubclassDelegator(self.base)

