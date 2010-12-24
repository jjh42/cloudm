import unittest
from cloudm import cloudmemoize,memmemoize
import inspect
import random

class MemoizeDecorator(object):
    """Generic testing for a decorating. Use setUp to set self.decorator for testing."""
    def test_simple_fn(self):
        @self.decorator
        def foo(x):
            return x
        self.assertEqual(foo(3), 3)
        self.assertEqual(foo(4), 4)

    def test_fn_name_args(self):
        @self.decorator
        def foobar(x,y=None):
            return (x,y)
        n = random.random()

        self.assertEqual(foobar(n), (n,None))
        self.assertEqual(foobar(n,5), (n,5))
        self.assertEqual(foobar(n,5), (n,5))
        self.assertEqual(foobar(n,5), (n,5))

    def test_class(self):
        class foo():
            def __init__(self, x):
                self.x = x
            
            @self.decorator
            def getx(self,y):
                return self.x

        f = foo(3)
        self.assertEqual(f.getx(y=4), 3)

    def test_docstring(self):
        @self.decorator
        def foobar():
            """Doc string"""

        self.assertEqual(foobar.__doc__, "Doc string")

    def test_argspec(self):
        @self.decorator
        def a():
            """foo"""
        def b():
            """foo"""

        self.assertEqual(inspect.getargspec(a), inspect.getargspec(b))


class TestCloudMemoizer(MemoizeDecorator, unittest.TestCase):
    def setUp(self):
        super(TestCloudMemoizer, self).setUp()
        self.decorator = cloudmemoize

class TestMemMemoizer(MemoizeDecorator, unittest.TestCase):
    def setUp(self):
        super(TestMemMemoizer, self).setUp()
        self.decorator = memmemoize
