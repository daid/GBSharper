from ..handler import handler
from ...pseudo import *
from ..code import Code
from ..register import RegisterAllocator


ARITHMETIC_ASM = {
    '+': 'add', '-': 'sub', '&': 'and', '|': 'or', '^': 'xor'
}
@handler(8, OP_ARITHMETIC)
def op_handler(code: Code, ra: RegisterAllocator, op):
    r0 = ra.get(op.args[1])
    if ra.get(op.args[2]) == "A" and op.args[0] in {'+', '&', '|', '^'}:
        # If the destination is not "A" but the source is, we can swap source and destination for addition
        r1 = ra.get(op.args[2])
        code.add(f"{ARITHMETIC_ASM[op.args[0]]} {r1}, {r0}")
        ra.reg_replaced_by(op.args[1], op.args[2])
        return True
    if r0 != 'A':
        r0 = ra.move_reg(r0, "A")
    r1 = ra.get(op.args[2])
    code.add(f"{ARITHMETIC_ASM[op.args[0]]} {r0}, {r1}")
    ra.free(op.args[2])
    return True


@handler(8, OP_LOAD, OP_ARITHMETIC)
def op_arithmetic_by_HL(code: Code, ra: RegisterAllocator, load, arithmetic):
    if not ra.is_free("H", "L"):
        return False
    if load.args[0] != arithmetic.args[2] or arithmetic.args[0] not in {'+', '-', '&', '|', '^'}:
        return False
    r0 = ra.get(arithmetic.args[1])
    if r0 != 'A':
        r0 = ra.move_reg(r0, "A")
    code.add(f"ld HL, _{load.args[1]}")
    code.add(f"{ARITHMETIC_ASM[arithmetic.args[0]]} {r0}, [HL]")
    return True


@handler(8, OP_LOAD_VALUE, OP_ARITHMETIC)
def op_arithmetic_constant(code: Code, ra: RegisterAllocator, load, arithmetic):
    if load.args[0] != arithmetic.args[2] or arithmetic.args[0] not in {'+', '-', '&', '|', '^'}:
        return False
    r0 = ra.get(arithmetic.args[1])
    if r0 != 'A':
        r0 = ra.move_reg(r0, "A")
    code.add(f"{ARITHMETIC_ASM[arithmetic.args[0]]} {r0}, {load.args[1]&0xFF}")
    return True
