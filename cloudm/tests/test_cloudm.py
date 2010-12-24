import unittest
from cloudm import cloudmemoize
import inspect

class TestCloudM(unittest.TestCase):
    def test_simple_fn(self):
        @cloudmemoize
        def foo(x):
            return x

        self.assertEqual(foo(3), 3)
        self.assertEqual(foo(4), 4)

    def test_fn_name_args(self):
        @cloudmemoize
        def foobar(x,y=None):
            return (x,y)

        self.assertEqual(foobar(3), (3,None))
        self.assertEqual(foobar(3,5), (3,5))

    def test_class(self):
        class foo():
            def __init__(self, x):
                self.x = x
            
            @cloudmemoize
            def getx(self,y):
                return self.x

        f = foo(3)
        self.assertEqual(f.getx(y=4), 3)

    def test_docstring(self):
        @cloudmemoize
        def foobar():
            """Doc string"""

        self.assertEqual(foobar.__doc__, "Doc string")

    def test_argspec(self):
        @cloudmemoize
        def a():
            """foo"""
        def b():
            """foo"""

        self.assertEqual(inspect.getargspec(a), inspect.getargspec(b))
