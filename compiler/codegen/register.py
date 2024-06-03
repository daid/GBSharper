from typing import Set

from ..pseudo import *
from .code import Code

FLAG_ALU_RESULT = 1
REG_TO_IDX = {"A": 7, "B": 0, "C": 1, "D": 2, "E": 3, "H": 4, "L": 5}
ALL_REGS = "BCDEHLA"
ALL_REGS16 = ["BC", "DE", "HL"]


class RegisterAllocator:
    def __init__(self, code: Code):
        self._code = code
        self._flags = {}
        self._free_regs = {"A", "B", "C", "D", "E", "H", "L"}
        self._alloc = {}
        self._reg_is = {}

    def set_alu_result(self, nr: int) -> None:
        self._flags[nr] = self._flags.get(nr, 0) | FLAG_ALU_RESULT

    def alloc(self, nr: int) -> str:
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

    def alloc16(self, nr: int) -> str:
        assert nr not in self._alloc
        flags = self._flags.get(nr, 0)
        allowed = {"BC", "DE", "HL"}
        if flags & FLAG_ALU_RESULT:
            allowed = {"HL"}
        options = {opt for opt in allowed if opt[0] in self._free_regs and opt[1] in self._free_regs}
        if not options and self._free_regs:
            raise NotImplementedError(f"Want {allowed} but free: {self._free_regs} (flags: {flags})")
        else:
            pick = self._pick_best_reg16(options)
        self._alloc[nr] = pick
        self._reg_is[pick[0]] = nr
        self._reg_is[pick[1]] = nr
        self._free_regs.remove(pick[0])
        self._free_regs.remove(pick[1])
        return pick

    def is_free(self, *regs) -> bool:
        for reg in regs:
            if reg not in self._free_regs:
                return False
        return True

    def free(self, nr):
        reg = self._alloc[nr]
        if len(reg) == 2:
            self._reg_is.pop(reg[0])
            self._reg_is.pop(reg[1])
            self._alloc.pop(nr)
            self._free_regs.add(reg[0])
            self._free_regs.add(reg[1])
        else:
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

    def reg_replaced_by(self, source, target):
        self.free(source)
        self._alloc[source] = self._alloc[target]
        self._alloc.pop(target)
        self._reg_is[target] = self._alloc[source]

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

    def _pick_best_reg16(self, options: Set[str]):
        for reg in ALL_REGS16:
            if reg in options:
                return reg
        raise RuntimeError("Picking best reg from empty set?")
