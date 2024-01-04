import unittest

from compiler.compiler import Compiler
from sim.testcpu import TestCPU


class Result:
    def __init__(self, cpu: TestCPU, symbols):
        self.__cpu = cpu
        self.__symbols = symbols

    def __getattr__(self, item):
        addr, bank = self.__symbols[f"_{item.upper()}"]
        return self.__cpu.read(addr)


def compile_and_run(code):
    c = Compiler()
    c.add_module("code", code)
    rom, symbols = c.build()
    cpu = TestCPU(rom)
    for n in range(1000000):
        cpu.step()
        if cpu.hard_halt:
            break
    return Result(cpu, symbols)


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
