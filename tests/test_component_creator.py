import unittest
from pynetsym.util.component_creator import ComponentCreator, ComponentError

class AttrMock(object):
    def __init__(self, **kwargs):
        vars(self).update(**kwargs)


class AbstractComponentCreatorT(object):
    def setUp(self):
        self.component_name = 'foo'
        self.options = ['a', 'b']
        self.values = [1, 2]


    def override_options(self):
        return dict(zip(self.options, self.values))

    def test_component_creator_set(self):
        self.component_creator.build(self.override_options(),
                                     set_=True)
        self.assertTrue(hasattr(self.context, self.component_name))
        component = getattr(self.context, self.component_name)

        for option, value in zip(self.options, self.values):
            self.assertEqual(value, getattr(component, option))

    def test_component_creator(self):
        component = self.component_creator.build(self.override_options())
        for option, value in zip(self.options, self.values):
            self.assertEqual(value, getattr(component, option))


class TestComponentCreatorOptionsInContext(AbstractComponentCreatorT, unittest.TestCase):
    def setUp(self):
        super(TestComponentCreatorOptionsInContext, self).setUp()
        self.context = AttrMock(
                foo_options=self.options[:],
                foo_type=AttrMock)
        self.component_creator = ComponentCreator(
                self.context,
                self.component_name)

class TestComponentCreatorOptionsInObject(AbstractComponentCreatorT, unittest.TestCase):
    def setUp(self):
        super(TestComponentCreatorOptionsInObject, self).setUp()
        class SomeClass(AttrMock):
            options = self.options[:]

        self.context = AttrMock(foo_type=SomeClass)
        self.component_creator = ComponentCreator(
                self.context,
                self.component_name)

class TestComponentCreatorOptionsSomeStatic(AbstractComponentCreatorT, unittest.TestCase):
    def setUp(self):
        super(TestComponentCreatorOptionsSomeStatic, self).setUp()

        self.options.append('c')
        class SomeClass(AttrMock):
            options = self.options[:]

        self.context = AttrMock(
                foo_type=SomeClass,
                foo_parameters=dict(zip(self.options[:-1], self.values)))
        self.component_creator = ComponentCreator(
                self.context,
                self.component_name)
        self.values[1:] = (3, 4)

    def override_options(self):
        return dict(zip(self.options[1:], self.values[1:]))

class TestComponentCreatorIntrospection(AbstractComponentCreatorT, unittest.TestCase):
    def setUp(self):
        super(TestComponentCreatorIntrospection, self).setUp()

        class SomeClass(AttrMock):
            def __init__(self, a, b):
                super(SomeClass, self).__init__(a=a, b=b)

        self.context = AttrMock(foo_type=SomeClass)
        self.component_creator = ComponentCreator(
            self.context, self.component_name)



class TestComponentCreatorNotEnoughArguments(unittest.TestCase):
    def setUp(self):
        self.component_name = 'foo'
        self.options = ['a', 'b']
        self.values = [1, 2]

        class SomeClass(AttrMock):
            def __init__(self, a, b, c):
                super(SomeClass, self).__init__(a=a, b=b, c=c)

        self.context = AttrMock(foo_type=SomeClass)
        self.component_creator = ComponentCreator(
            self.context, self.component_name)

    def test_component_creator(self):
        self.assertRaises(ComponentError, self.component_creator.build,
                          self.override_options())

    def override_options(self):
        return dict(zip(self.options, self.values))

class TestComponentCreatorAdditional(unittest.TestCase):
    def setUp(self):
        self.component_name = 'foo'
        self.options = ['a', 'b']
        self.values = [1, 2]

        class SomeClass(AttrMock):
            def __init__(self, a, *b):
                super(SomeClass, self).__init__(a=a, b=b)

        self.context = AttrMock(foo_type=SomeClass)
        self.component_creator = ComponentCreator(
            self.context, self.component_name)

    def test_component_creator(self):
        self.assertRaises(ComponentError, self.component_creator.build,
                          self.override_options())

    def override_options(self):
        return dict(zip(self.options, self.values))

class TestComponentCreatorKeyword(AbstractComponentCreatorT, unittest.TestCase):
    def setUp(self):
        self.component_name = 'foo'
        self.options = ['a', 'b']
        self.values = [1, 2]

        class SomeClass(AttrMock):
            def __init__(self, a, **kw):
                super(SomeClass, self).__init__(a=a, **kw)

        self.context = AttrMock(foo_type=SomeClass)
        self.component_creator = ComponentCreator(
            self.context, self.component_name)

    def override_options(self):
        return dict(zip(self.options, self.values))