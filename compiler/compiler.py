from typing import Dict

from .assembler import Assembler
from .astnode import AstNode
from .codegen import gen_code
from .exception import CompileException
from .parse.function import Function
from .parse.parser import parse
from .pseudo import PseudoState


class Compiler:
    def __init__(self):
        self.consts: Dict[str, AstNode] = {}
        self.vars: Dict[str, AstNode] = {}
        self.funcs: Dict[str, Function] = {}

    def add_file(self, filename):
        module = parse(filename, open(filename, "rt").read())
        for const in module.consts:
            if const.token.value in self.consts:
                raise CompileException(const.token, "Duplicate const definition")
            self.consts[const.token.value] = const
        for var in module.vars:
            if var.token.value in self.consts:
                raise CompileException(var.token, "Duplicate const definition")
            self.vars[var.token.value] = var
        for func in module.funcs:
            if func.token.value in self.consts:
                raise CompileException(func.token, "Duplicate const definition")
            self.funcs[func.token.value] = func

    def build(self):
        code = ""
        for name, func in self.funcs.items():
            ps = PseudoState(func)
            code += f"_{func.name}:\n"
            code += gen_code(ps)
            code += "ret\n"
        asm = Assembler()
        asm.addConstant("_X", 0xC000)
        asm.addConstant("_Y", 0xC001)
        asm.process("jp std_start\nds $150-3", base_address=0x0100, bank=0) # Reserve header area
        asm.process(open("stdlib/start.asm", "rt").read(), base_address=-2, bank=0)
        asm.process(open("stdlib/logic.asm", "rt").read(), base_address=-2, bank=0)
        asm.process(code, base_address=-2)
        asm.link()

        rom_data = bytearray(0x10000)
        for s in asm.getSections():
            while s.bank * 0x4000 >= len(rom_data):
                rom_data += bytearray(0x4000)
            start = s.bank * 0x4000 + (s.base_address & 0x3FFF)
            rom_data[start:start+len(s.data)] = s.data
        for label, addr, bank in asm.getLabels():
            print(f"{bank:02x}:{addr:04x} {label}")
        # Fix the header
        rom_data[0x0104:0x0134] = b'\xCE\xED\x66\x66\xCC\x0D\x00\x0B\x03\x73\x00\x83\x00\x0C\x00\x0D\x00\x08\x11\x1F\x88\x89\x00\x0E\xDC\xCC\x6E\xE6\xDD\xDD\xD9\x99\xBB\xBB\x67\x63\x6E\x0E\xEC\xCC\xDD\xDC\x99\x9F\xBB\xB9\x33\x3E'
        rom_data[0x0143] = 0 # GBC flag
        rom_data[0x0147] = 0 # Cart type
        rom_data[0x0148] = 0 # ROM size
        rom_data[0x0149] = 0 # SRAM size
        checksum = 0
        for b in rom_data[0x0134:0x14D]:
            checksum -= b + 1
        rom_data[0x14D] = checksum & 0xFF
        checksum = sum(rom_data)
        rom_data[0x14E] = (checksum >> 8) & 0xFF
        rom_data[0x14F] = checksum & 0xFF
        return rom_data
