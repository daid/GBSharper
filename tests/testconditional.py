import unittest
from .util import compile_and_run


class TestConditional(unittest.TestCase):
    def test_simple_if(self):
        res = compile_and_run("""
var x = 0

fn main
    x = 10
    if x
        x = 20
""")
        self.assertEqual(res.x, 20)

    def test_simple_not_if(self):
        res = compile_and_run("""
var x = 0

fn main
    if x
        x = 20
""")
        self.assertEqual(res.x, 0)

    def test_less(self):
        res = compile_and_run("""
var x = 5
var y = 10
var z = 0

fn main
    if x < y
        z = 20
""")
        self.assertEqual(res.z, 20)

    def test_not_else(self):
        res = compile_and_run("""
var x = 5
var z = 0

fn main
    if x
        z = 20
    else
        z = 30
""")
        self.assertEqual(res.z, 20)

    def test_else(self):
        res = compile_and_run("""
var x = 0
var z = 0

fn main
    if x
        z = 20
    else
        z = 30
""")
        self.assertEqual(res.z, 30)
