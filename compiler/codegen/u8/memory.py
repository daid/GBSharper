from ..handler import handler
from ...pseudo import *
from ..code import Code
from ..register import RegisterAllocator


@handler(8, OP_LOAD)
def op_handler(code: Code, ra: RegisterAllocator, op):
    r0 = ra.alloc(op.args[0])
    if r0 != "A":
        r0 = ra.move_reg(r0, "A")
    code.add(f"ld {r0}, [_{op.args[1]}]")
    return True


@handler(8, OP_LOAD_VALUE)
def op_handler(code: Code, ra: RegisterAllocator, op):
    r0 = ra.alloc(op.args[0])
    if r0 == "A" and (op.args[1]&0xFF) == 0:
        code.add(f"xor {r0}")
    else:
        code.add(f"ld {r0}, {op.args[1]&0xFF}")
    return True


@handler(8, OP_STORE)
def op_handler(code: Code, ra: RegisterAllocator, op):
    r0 = ra.get(op.args[0])
    if r0 != "A":
        r0 = ra.move_reg(r0, "A")
    code.add(f"ld [_{op.args[1]}], {r0}")
    ra.free(op.args[0])
    return True
