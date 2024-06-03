import unittest
from .util import compile_and_run


class TestFunc(unittest.TestCase):
    def test_call(self):
        res = compile_and_run("""
var x = 0

fn main
    f1()

fn f1
    x = 10
""")
        self.assertEqual(res.x, 10)

    def test_call2(self):
        res = compile_and_run("""
var x = 0
var y = 0

fn main
    f1()
    f2()

fn f1
    x = 10
fn f2
    y = 17
""")
        self.assertEqual(res.x, 10)
        self.assertEqual(res.y, 17)

    def test_param(self):
        res = compile_and_run("""
var x = 0

fn main
    f1(10)

fn f1 y
    x = y + 15
""")
        self.assertEqual(res.x, 25)

    def test_param2(self):
        res = compile_and_run("""
var x = 1

fn main
    f1(20, 5)

fn f1 y z
    x = y - z
""")
        self.assertEqual(res.x, 15)

    def test_return(self):
        res = compile_and_run("""
var x = 1

fn main
    x = f1(4)

fn f1 y > u8
    return y + 1
""")
        self.assertEqual(res.x, 5)

    def test_return_unused(self):
        res = compile_and_run("""
var x = 1

fn main
    f1(4)

fn f1 y > u8
    x = y
    return y + 1
""")
        self.assertEqual(res.x, 4)
