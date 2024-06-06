from ..handler import handler
from ...pseudo import *
from ..code import Code
from ..register import RegisterAllocator


ARITHMETIC_ASM = {
    '+': ('add', 'adc'), '-': ('sub', 'sbc'), '&': ('and', 'and'), '|': ('or', 'or'), '^': ('xor', 'xor')
}
@handler(16, OP_ARITHMETIC)
def op_handler(code: Code, ra: RegisterAllocator, op):
    if op.args[0] not in {'+', '-', '&', '|', '^'}:
        return False
    r0 = ra.get(op.args[1])
    r1 = ra.get(op.args[2])
    if op.args[0] == '+' and r0 == "HL":
        code.add(f"add {r0}, {r1}")
    else:
        if not ra.is_free("A"):
            raise RuntimeError("Need A")
        code.add(f"ld A, {r0[1]}")
        code.add(f"{ARITHMETIC_ASM[op.args[0]][0]} A, {r1[1]}")
        code.add(f"ld {r0[1]}, A")
        code.add(f"ld A, {r0[0]}")
        code.add(f"{ARITHMETIC_ASM[op.args[0]][1]} A, {r1[0]}")
        code.add(f"ld {r0[0]}, A")
    ra.free(op.args[2])
    return True


@handler(16, OP_LOAD_VALUE, OP_ARITHMETIC)
def op_arithmetic_constant(code: Code, ra: RegisterAllocator, load, arithmetic):
    if load.args[0] != arithmetic.args[2] or arithmetic.args[0] != '*':
        return False
    r0 = ra.get(arithmetic.args[1])
    if r0 != "HL":
        return False
    if load.args[1] in {0, 1, 2, 4, 8, 16, 32, 64, 128}:
        n = load.args[1]
        while n > 0:
            code.add(f"add {r0}, {r0}")
            n //= 2
    return True
