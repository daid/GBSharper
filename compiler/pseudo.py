from typing import List

from .astnode import AstNode
from .exception import CompileException
from .parse.function import Function

OP_LOAD = 0
OP_LOAD_VALUE = 1
OP_STORE = 2
OP_ARITHMETIC = 3
OP_LOGIC = 4
OP_LABEL = 5
OP_JUMP = 6
OP_JUMP_ZERO = 7
OP_COMPLEMENT = 8
OP_SHIFT = 9
OP_NAMES = ["LOAD", "LOADV", "STORE", "ARITHETIC", "LOGIC", "LABEL", "JUMP", "JUMP_ZERO", "COMPLEMENT", "SHIFT"]


class PseudoOp:
    def __init__(self, kind, *args):
        self.kind = kind
        self.args = args

    def __repr__(self):
        return f"{OP_NAMES[self.kind]}: {self.args}"


class PseudoState:
    def __init__(self, func: Function):
        self.ops: List[PseudoOp] = []
        self._reg_count = 0
        self._free_regs = []
        self._label_nr = 0
        self.block(func.block)
        assert len(self._free_regs) == self._reg_count

    def block(self, block):
        for node in block:
            r = self.step(node)
            if r != -1:
                self.free_reg(r)

    def new_reg(self):
        self._reg_count += 1
        return self._reg_count

    def free_reg(self, r):
        self._free_regs.append(r)

    def step(self, node: AstNode):
        r0 = -1
        if node.kind == '=':
            r1 = self.step(node.params[1])
            self.ops.append(PseudoOp(OP_STORE, r1, node.params[0].token.value))
            self.free_reg(r1)
        elif node.kind in {'U-'}:
            r0 = self.step(node.params[0])
            self.ops.append(PseudoOp(OP_COMPLEMENT, r0))
        elif node.kind in {'+', '-', '*', '/', '%'}:
            r0 = self.step(node.params[0])
            r1 = self.step(node.params[1])
            self.ops.append(PseudoOp(OP_ARITHMETIC, node.kind, r0, r1))
            self.free_reg(r1)
        elif node.kind in {'<', '>', '==', '!='}:
            r0 = self.step(node.params[0])
            r1 = self.step(node.params[1])
            self.ops.append(PseudoOp(OP_LOGIC, node.kind, r0, r1))
            self.free_reg(r1)
        elif node.kind == 'SHIFT':
            r0 = self.step(node.params[0])
            r1 = self.step(node.params[1])
            self.ops.append(PseudoOp(OP_SHIFT, node.token.value, r0, r1))
            self.free_reg(r1)
        elif node.kind == 'ID':
            r0 = self.new_reg()
            self.ops.append(PseudoOp(OP_LOAD, r0, node.token.value))
        elif node.kind == 'NUM':
            r0 = self.new_reg()
            self.ops.append(PseudoOp(OP_LOAD_VALUE, r0, node.token.value))
        elif node.kind == 'IF':
            r1 = self.step(node.params[0])
            if_label = self.next_label()
            self.ops.append(PseudoOp(OP_JUMP_ZERO, if_label, r1))
            self.free_reg(r1)
            self.block(node.params[1].params)
            if len(node.params) > 2:
                end_label = self.next_label()
                self.ops.append(PseudoOp(OP_JUMP, end_label))
                self.ops.append(PseudoOp(OP_LABEL, if_label))
                self.block(node.params[2].params)
                self.ops.append(PseudoOp(OP_LABEL, end_label))
            else:
                self.ops.append(PseudoOp(OP_LABEL, if_label))
        else:
            raise CompileException(node.token, f"Do not know how to convert {node} into pseudo ops")
        return r0

    def next_label(self):
        self._label_nr += 1
        return self._label_nr
