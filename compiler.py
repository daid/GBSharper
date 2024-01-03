from typing import Dict

from assembler import Assembler
from astnode import AstNode
from codegen import gen_code
from exception import CompileException
from parse.function import Function
from parse.parser import parse
from pseudo import PseudoState


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
        asm.addConstant("_Y", 0xC000)
        asm.process(open("stdlib/logic.asm", "rt").read(), base_address=0, bank=0)
        asm.process(code, base_address=0x4000, bank=1)
        asm.link()
        for s in asm.getSections():
            print(s)
        for label, addr, bank in asm.getLabels():
            print(f"{bank:02x}:{addr:04x} {label}")