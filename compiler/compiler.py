from typing import Dict
import os

from .assembler import Assembler
from .astnode import AstNode
from .codegen.generator import gen_code
from .exception import CompileException
from .parse.parser import parse
from .pseudo import PseudoState
from .scope import Scope


class Compiler:
    def __init__(self):
        self.consts: Dict[str, AstNode] = {}
        self.main_scope = Scope("global_var")

    def add_file(self, filename: str):
        self.add_module(filename, open(filename, "rt").read())

    def add_module(self, name: str, code: str):
        module = parse(name, code)
        for const in module.consts:
            if const.token.value in self.consts:
                raise CompileException(const.token, "Duplicate const definition")
            self.consts[const.token.value] = const
        for var in module.vars:
            if var.token.value in self.consts:
                raise CompileException(var.token, "Duplicate variable definition")
            self.main_scope.vars[var.token.value] = var
        for func in module.funcs:
            if func.token.value in self.consts:
                raise CompileException(func.token, "Duplicate function definition")
            self.main_scope.funcs[func.token.value] = func

    def dump_ast(self):
        for func in self.main_scope.funcs.values():
            func.dump()

    def build(self, *, print_asm_code=False):
        asm = Assembler()
        asm.process("jp std_start\nds $150-3", base_address=0x0100, bank=0) # Reserve header area
        for f in os.listdir("stdlib"):
            fp = open(f"stdlib/{f}", "rt")
            asm.process(fp.read(), base_address=-2, bank=0)
            fp.close()
        ram_code = ""
        init_code = "__init:\n"
        for name, var in self.main_scope.vars.items():
            ram_code += f"_{self.main_scope.prefix}_{name}:\n ds {var.data_type.size//8}\n"
            init_code += f"ld a, {var.params[0].token.value}\nld [_{self.main_scope.prefix}_{name}], a\n"
        # TODO: Figure out call tree and overlap function parameters where possible.
        for name, func in self.main_scope.funcs.items():
            for param in func.parameters:
                ram_code += f"_local_{func.name}_{param.name}:\n ds {param.vartype.size//8}\n"
        asm.process(ram_code, base_address=0xC000, bank=0)
        asm.process(init_code + "ret", base_address=-2, bank=1)
        for name, func in self.main_scope.funcs.items():
            scope = Scope(f"local_{name}", self.main_scope)
            for param in func.parameters:
                scope.vars[param.name] = param.vartype
            ps = PseudoState(scope, func)
            code = f"_function_{func.name}:\n"
            code += gen_code(ps)
            code += "ret\n"
            if print_asm_code:
                print(code)
            asm.process(code, base_address=-2)
        asm.link()

        rom_data = bytearray(0x10000)
        for s in asm.getSections():
            if s.base_address >= 0x8000:
                assert s.data.count(0) == len(s.data)
                continue
            while s.bank * 0x4000 >= len(rom_data):
                rom_data += bytearray(0x4000)
            start = s.bank * 0x4000 + (s.base_address & 0x3FFF)
            rom_data[start:start+len(s.data)] = s.data

        # for label, addr, bank in asm.getLabels():
        #     print(f"{bank:02x}:{addr:04x} {label}")

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
        return rom_data, {l: (a, b) for l, a, b in asm.getLabels()}
