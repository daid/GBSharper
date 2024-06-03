from ..handler import handler
from ...pseudo import *
from ..code import Code
from ..register import RegisterAllocator


@handler(16, OP_LOAD)
def op_handler(code: Code, ra: RegisterAllocator, op):
    if not ra.is_free("A"):
        return False
    r0 = ra.alloc16(op.args[0])
    code.add(f"ld A, [_{op.args[1]}]")
    code.add(f"ld {r0[0]}, A")
    code.add(f"ld A, [_{op.args[1]}+1]")
    code.add(f"ld {r0[1]}, A")
    return True


@handler(16, OP_LOAD_VALUE)
def op_handler(code: Code, ra: RegisterAllocator, op):
    r0 = ra.alloc16(op.args[0])
    code.add(f"ld {r0}, {op.args[1]&0xFFFF}")
    return True


@handler(16, OP_STORE)
def op_handler(code: Code, ra: RegisterAllocator, op):
    if not ra.is_free("A"):
        return False
    r0 = ra.get(op.args[0])
    code.add(f"ld A, {r0[0]}")
    code.add(f"ld [_{op.args[1]}], A")
    code.add(f"ld A, {r0[1]}")
    code.add(f"ld [_{op.args[1]}+1], A")
    ra.free(op.args[0])
    return True
