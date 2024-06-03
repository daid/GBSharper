from ..pseudo import *
from .code import Code
from .register import RegisterAllocator
from .handler import handler, get_handlers


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


@handler(8, OP_LOGIC)
def op_handler(code: Code, ra: RegisterAllocator, op):
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
    return True


@handler(8, OP_COMPLEMENT)
def op_handler(code: Code, ra: RegisterAllocator, op):
    r0 = ra.get(op.args[0])
    if r0 != 'A':
        r0 = ra.move_reg(r0, "A")
    assert r0 == 'A'
    code.add(f"cpl")
    return True


@handler(8, OP_LOAD_VALUE, OP_SHIFT)
def op_arithmetic_constant(code: Code, ra: RegisterAllocator, load, shift):
    if load.args[0] != shift.args[2]:
        return False
    r0 = ra.get(shift.args[1])
    amount = load.args[1]
    if amount < 0:
        return False

    if shift.args[0] == '>>':
        for n in range(amount):
            code.add(f"srl {r0}")
    elif shift.args[0] == '<<':
        for n in range(amount):
            code.add(f"sla {r0}")
    else:
        raise RuntimeError(f"No codegen implementation for {shift}")
    return True


@handler(8, OP_SHIFT)
def op_handler(code: Code, ra: RegisterAllocator, op):
    r0 = ra.get(op.args[1])
    r1 = ra.get(op.args[2])
    if op.args[0] == "<<":
        code.add(f"sla {r0}")
    elif op.args[0] == ">>":
        code.add(f"srl {r0}")
    else:
        raise RuntimeError(f"No codegen implementation for {op}")
    raise RuntimeError(f"No codegen implementation for {op}")


@handler(0, OP_JUMP)
def op_handler(code: Code, ra: RegisterAllocator, op):
    code.add(f"jpr ._{op.args[0]}")
    return True


@handler(8, OP_JUMP_ZERO)
def op_handler(code: Code, ra: RegisterAllocator, op):
    r0 = ra.get(op.args[1])
    code.add(f"and {r0}, {r0}")
    ra.free(op.args[1])
    code.add(f"jpr z, ._{op.args[0]}")
    return True


@handler(0, OP_CALL)
def op_handler(code: Code, ra: RegisterAllocator, op):
    code.add(f"call _function_{op.args[0]}")
    return True


@handler(0, OP_RETURN)
def op_handler(code: Code, ra: RegisterAllocator, op):
    code.add(f"ret")
    return True


def gen_code(ps: PseudoState):
    code = Code()
    ra = RegisterAllocator(code)
    for op in ps.ops:
        if op.kind in {OP_ARITHMETIC, OP_LOGIC, OP_JUMP_ZERO}:
            ra.set_alu_result(op.args[1])
        if op.kind in {OP_LOAD, OP_STORE}:
            ra.set_alu_result(op.args[0])
    idx = 0
    while idx < len(ps.ops):
        op = ps.ops[idx]
        if op.kind == OP_LABEL:
            code.add(f"._{op.args[0]}:")
            idx += 1
        else:
            done = False
            for h in get_handlers(op):
                ops = ps.ops[idx+1:idx+1+len(h.ops)]
                if ops_match(ops, h.ops) and h(code, ra, op, *ops):
                    code.comment(f"{op}")
                    for o in ops:
                        code.comment(f"{o}")
                    done = True
                    idx += 1 + len(ops)
                    break
            if not done:
                raise RuntimeError(f"No codegen implementation for {op}")
        code.finish()
    return code.code

def ops_match(ops, target_ops):
    if len(ops) != len(target_ops):
        return False
    for a, b in zip(ops, target_ops):
        if a.kind != b:
            return False
    return True
