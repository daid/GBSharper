from ..pseudo import *
from .code import Code
from .register import RegisterAllocator


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
        elif op.kind == OP_CALL:
            code.add(f"call _function_{op.args[0]}")
        else:
            raise RuntimeError(f"No codegen implementation for {op}")
    return code.code
