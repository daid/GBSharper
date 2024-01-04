import unittest
from .util import compile_and_run


class TestMath(unittest.TestCase):
    def test_assign(self):
        res = compile_and_run("""
var x = 0

fn main
    x = 10
""")
        self.assertEqual(res.x, 10)

    def test_assign2(self):
        res = compile_and_run("""
var x = 12
var y = 0

fn main
    y = x
""")
        self.assertEqual(res.y, 12)

    def test_add8(self):
        res = compile_and_run("""
var x = 2
var y = 3

fn main
    x = x + y
""")
        self.assertEqual(res.x, 5)

    def test_sub8(self):
        res = compile_and_run("""
var x = 5
var y = 3

fn main
    x = x - y
""")
        self.assertEqual(res.x, 2)
