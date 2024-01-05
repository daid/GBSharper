from typing import Set

from .pseudo import *

FLAG_ALU_RESULT = 1
REG_TO_IDX = {"A": 7, "B": 0, "C": 1, "D": 2, "E": 3, "H": 4, "L": 5}
ALL_REGS = "BCDEHLA"


class Code:
    def __init__(self):
        self.code = ""

    def add(self, line):
        self.code += line + "\n"


class RegisterAllocator:
    def __init__(self, code: Code):
        self._code = code
        self._flags = {}
        self._free_regs = {"A", "B", "C", "D", "E", "H", "L"}
        self._alloc = {}
        self._reg_is = {}

    def set_alu_result(self, nr):
        self._flags[nr] = self._flags.get(nr, 0) | FLAG_ALU_RESULT

    def alloc(self, nr):
        assert nr not in self._alloc
        flags = self._flags.get(nr, 0)
        allowed = {"A", "B", "C", "D", "E", "H", "L"}
        if flags & FLAG_ALU_RESULT:
            allowed = {"A"}
        options = allowed.intersection(self._free_regs)
        if not options and self._free_regs:
            # Move an allowed reg to a free reg
            pick = self._pick_best_reg(allowed)
            self._move_reg(pick, self._pick_best_reg(self._free_regs))
        else:
            pick = self._pick_best_reg(options)
        self._alloc[nr] = pick
        self._reg_is[pick] = nr
        self._free_regs.remove(pick)
        return pick

    def free(self, nr):
        reg = self._alloc[nr]
        self._reg_is.pop(reg)
        self._alloc.pop(nr)
        self._free_regs.add(reg)

    def get(self, nr):
        return self._alloc[nr]

    def move_reg(self, from_reg, to_reg):
        if to_reg not in self._free_regs:
            self._move_reg(to_reg, self._pick_best_reg(self._free_regs))
        self._move_reg(from_reg, to_reg)
        return to_reg

    def _move_reg(self, from_reg, to_reg):
        self._code.add(f"ld {to_reg}, {from_reg}")
        nr = self._reg_is.pop(from_reg)
        self._alloc.pop(nr)
        self._free_regs.add(from_reg)
        self._alloc[nr] = to_reg
        self._reg_is[to_reg] = nr
        self._free_regs.remove(to_reg)

    def _pick_best_reg(self, options: Set[str]):
        for reg in ALL_REGS:
            if reg in options:
                return reg
        raise RuntimeError("Picking best reg from empty set?")


def gen_code(ps: PseudoState):
    code = Code()
    ra = RegisterAllocator(code)
    for op in ps.ops:
        if op.kind in {OP_ARITHMETIC, OP_LOGIC, OP_JUMP_ZERO}:
            ra.set_alu_result(op.args[1])
        if op.kind in {OP_LOAD, OP_STORE}:
            ra.set_alu_result(op.args[0])
    for op in ps.ops:
        code.add(f"; {op}")
        if op.kind == OP_LOAD:
            r0 = ra.alloc(op.args[0])
            if r0 != "A":
                r0 = ra.move_reg(r0, "A")
            code.add(f"ld {r0}, [_{op.args[1]}]")
        elif op.kind == OP_LOAD_VALUE:
            code.add(f"ld {ra.alloc(op.args[0])}, {op.args[1]}")
        elif op.kind == OP_STORE:
            r0 = ra.get(op.args[0])
            if r0 != "A":
                r0 = ra.move_reg(r0, "A")
            code.add(f"ld [_{op.args[1]}], {r0}")
            ra.free(op.args[0])
        elif op.kind == OP_ARITHMETIC:
            r0 = ra.get(op.args[1])
            if r0 != 'A':
                r0 = ra.move_reg(r0, "A")
            r1 = ra.get(op.args[2])
            if op.args[0] == '+':
                code.add(f"add {r0}, {r1}")
            elif op.args[0] == '-':
                code.add(f"sub {r0}, {r1}")
            else:
                raise RuntimeError(f"No codegen implementation for {op}")
            ra.free(op.args[2])
        elif op.kind == OP_LOGIC:
            r0 = ra.get(op.args[1])
            if r0 != 'A':
                r0 = ra.move_reg(r0, "A")
            r1 = ra.get(op.args[2])
            code.add(f"cp {r0}, {r1}")
            if op.args[0] == "==":
                code.add("call __logic_equal")
            elif op.args[0] == "!=":
                code.add("call __logic_not_equal")
            elif op.args[0] == "<":
                code.add("call __logic_less")
            elif op.args[0] == ">":
                code.add("call __logic_greater")
            else:
                raise RuntimeError(f"No codegen implementation for {op}")
            ra.free(op.args[2])
        elif op.kind == OP_COMPLEMENT:
            r0 = ra.get(op.args[0])
            if r0 != 'A':
                r0 = ra.move_reg(r0, "A")
            assert r0 == 'A'
            code.add(f"cpl")
        elif op.kind == OP_SHIFT:
            r0 = ra.get(op.args[1])
            r1 = ra.get(op.args[2])
            if op.args[0] == "<<":
                code.add(f"sla {r0}")
            elif op.args[0] == ">>":
                code.add(f"srl {r0}")
            else:
                raise RuntimeError(f"No codegen implementation for {op}")
            raise RuntimeError(f"No codegen implementation for {op}")
        elif op.kind == OP_LABEL:
            code.add(f"._{op.args[0]}:")
        elif op.kind == OP_JUMP:
            code.add(f"jpr ._{op.args[0]}")
        elif op.kind == OP_JUMP_ZERO:
            r0 = ra.get(op.args[1])
            code.add(f"and {r0}, {r0}")
            ra.free(op.args[1])
            code.add(f"jpr z, ._{op.args[0]}")
        else:
            raise RuntimeError(f"No codegen implementation for {op}")
    return code.code
