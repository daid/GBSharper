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
