from compiler.compiler import Compiler
from sim.testcpu import MinimalCPU


class Result:
    def __init__(self, cpu: MinimalCPU, symbols):
        self.__cpu = cpu
        self.__symbols = symbols

    def __getattr__(self, item):
        addr, bank = self.__symbols[f"_GLOBAL_VAR_{item.upper()}"]
        for k, (a, b) in self.__symbols.items():
            if a == addr + 1:
                return self.__cpu.read(addr)
            if a == addr + 2:
                return self.__cpu.read(addr) | (self.__cpu.read(addr + 1) << 8)
        return None


def compile_and_run(code, max_cycles=10000):
    c = Compiler()
    c.add_module("code", code)
    rom, symbols = c.build(print_asm_code=True, print_pseudo_code=True)
    cpu = MinimalCPU(rom)
    cycles = 0
    while True:
        cpu.step()
        if cpu.hard_halt:
            break
        cycles += 1
        assert cycles < max_cycles, "Code never halts"
    return Result(cpu, symbols)
