import unittest
from cloudm import cloudmemoize


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
        self.assertEqual(f.getx(3, y=4), 3)
