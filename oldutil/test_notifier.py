from unittest import TestCase
from oldutil.notifications import notifier, notifies


@notifier
class A(object):
    INC = 'inc'
    DEC = 'dec'
    FOO = 'foo'
    BAR = 'bar'

    def __init__(self, foo, bar):
        self.foo = foo
        self.bar = bar

    @notifies(INC, FOO)
    def inc_foo(self):
        self.foo += 1

    @notifies(DEC, FOO)
    def dec_foo(self):
        self.foo -= 1

    @notifies(INC, BAR)
    def inc_bar(self):
        self.bar += 1

    @notifies(DEC, BAR)
    def dec_bar(self):
        self.bar -= 1


class TestNotifier(TestCase):
    def setUp(self):
        self.a = A(0, 0)
        self.make_checker(A.INC, A.BAR)
        self.make_checker(A.DEC, A.BAR)
        self.make_checker(A.INC, A.FOO)

    def testBase(self):
        self.a.inc_bar()
        self.a.dec_bar()
        self.a.inc_foo()
        self.a.dec_foo()  # I did not call any observer!

    def make_checker(self, event, kind):
        def checker(cevent, ckind, observed):
            self.assertEqual(event, cevent)
            self.assertEqual(kind, ckind)
            self.assertEqual(self.a, observed)

        self.a.register_observer(checker, event, kind)