from typing import Set

from ..pseudo import *
from .code import Code

FLAG_ALU_RESULT = 1
REG_TO_IDX = {"A": 7, "B": 0, "C": 1, "D": 2, "E": 3, "H": 4, "L": 5}
ALL_REGS = "BCDEHLA"


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
