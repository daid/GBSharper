import unittest
from .util import compile_and_run


class TestU16(unittest.TestCase):
    def test_cast_u8(self):
        res = compile_and_run("""
var x: u16 = 0x1234
var y: u8 = 1

fn main
    y = x as u8
""")
        self.assertEqual(res.y, 0x34)

    def test_cast_u16(self):
        res = compile_and_run("""
var x: u8 = 0x34
var y: u16 = 0x100

fn main
    y = x as u16
""")
        self.assertEqual(res.y, 0x34)
