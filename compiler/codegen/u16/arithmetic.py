from ..handler import handler
from ...pseudo import *
from ..code import Code
from ..register import RegisterAllocator


@handler(16, OP_ARITHMETIC)
def op_handler(code: Code, ra: RegisterAllocator, op):
    if op.args[0] != '+':
        return False
    r0 = ra.get(op.args[1])
    r1 = ra.get(op.args[2])
    code.add(f"add {r0}, {r1}")
    ra.free(op.args[2])
    return True
