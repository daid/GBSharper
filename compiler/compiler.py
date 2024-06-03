from typing import Dict
import os

from .assembler import Assembler
from .astnode import AstNode
from .codegen.generator import gen_code
from .exception import CompileException
from .parse.parser import parse
from .pseudo import PseudoState
from .scope import Scope, TopLevelScope
from .optimizer.constant import constant_collapse


class Compiler:
    def __init__(self):
        self.consts: Dict[str, int] = {}
        self.main_scope = TopLevelScope("global_var")

    def add_file(self, filename: str):
        self.add_module(filename, open(filename, "rt").read())

    def add_module(self, name: str, code: str):
        module = parse(name, code)
        for const in module.consts:
            constant_collapse(const.params[0])
            if const.token.value in self.consts:
                raise CompileException(const.token, f"Duplicate const definition: {const.token.value}")
            if const.params[0].kind != "NUM":
                raise CompileException(const.token, f"Const initialization is not a constant value: {const.token.value}")
            self.consts[const.token.value] = const.params[0].token.value
        for reg in module.regs:
            constant_collapse(reg.params[0])
            if reg.token.value in self.main_scope.regs or reg.token.value in self.consts:
                raise CompileException(reg.token, f"Duplicate reg definition: {reg.token.value}")
            if reg.params[0].kind != "NUM":
                raise CompileException(reg.token, f"Reg address is not a constant value: {reg.token.value}")
            self.main_scope.regs[reg.token.value] = reg
        for var in module.vars:
            if var.token.value in self.main_scope.vars or var.token.value in self.main_scope.regs or var.token.value in self.consts:
                raise CompileException(var.token, f"Duplicate variable definition: {var.token.value}")
            constant_collapse(var.params[0])
            if var.params[0].kind != "NUM":
                raise CompileException(var.token, f"Variable initialization is not a constant value: {var.token.value}")
            self.main_scope.vars[var.token.value] = var
        for func in module.funcs:
            if func.token.value in self.main_scope.funcs:
                raise CompileException(func.token, f"Duplicate function definition: {func.name}")
            for block in func.block:
                constant_collapse(block)
            self.main_scope.funcs[func.token.value] = func

    def dump_ast(self):
        for func in self.main_scope.funcs.values():
            func.dump()

    def build(self, *, print_asm_code=False, print_pseudo_code=False):
        asm = Assembler()
        asm.process("jp std_start\nds $150-3", base_address=0x0100, bank=0) # Reserve header area
        for f in os.listdir("stdlib"):
            fp = open(f"stdlib/{f}", "rt")
            asm.process(fp.read(), base_address=-2, bank=0)
            fp.close()
        ram_code = "__result__:\n ds 2\n"
        init_code = "__init:\n"
        for name, reg in self.main_scope.regs.items():
            ram_code += f"_{name} := {reg.params[0].token.value}\n"
        for name, var in self.main_scope.vars.items():
            ram_code += f"_{self.main_scope.prefix}_{name}:\n ds {var.data_type.size//8}\n"
            if var.data_type.size == 8:
                init_code += f"ld a, {var.params[0].token.value}\nld [_{self.main_scope.prefix}_{name}], a\n"
            else:
                init_code += f"ld a, {var.params[0].token.value&0xFF}\nld [_{self.main_scope.prefix}_{name}], a\n"
                init_code += f"ld a, {(var.params[0].token.value>>8)&0xFF}\nld [_{self.main_scope.prefix}_{name}+1], a\n"
        ram_code += "__ram_end:"
        # TODO: Figure out call tree and overlap function parameters where possible.
        for name, func in self.main_scope.funcs.items():
            for param in func.parameters:
                ram_code += f"_local_{func.name}_{param.token.value}:\n ds {param.data_type.size//8}\n"
            for var in func.vars:
                ram_code += f"_local_{func.name}_{var.token.value}:\n ds {var.data_type.size//8}\n"
        if print_asm_code:
            print(ram_code)
            print(init_code)
        asm.process(ram_code, base_address=0xC000, bank=0)
        asm.process(init_code + "ret", base_address=-2, bank=1)
        for name, func in self.main_scope.funcs.items():
            scope = Scope(f"local_{name}", self.main_scope)
            for param in func.parameters:
                scope.vars[param.token.value] = param
            for param in func.vars:
                scope.vars[var.token.value] = var
            ps = PseudoState(scope, func)
            if print_pseudo_code:
                for op in ps.ops:
                    print(op)
            code = f"_function_{func.name}:\n"
            code += gen_code(ps)
            if print_asm_code:
                print(code)
            asm.process(code, base_address=-2)
        asm.link()

        rom_data = bytearray(0x8000)
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
