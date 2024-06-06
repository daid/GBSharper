from typing import List

from .astnode import AstNode
from .exception import CompileException
from .parse.function import Function
from .scope import Scope
from .datatype import DataType, DEFAULT_TYPE

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
OP_CALL = 10
OP_RETURN = 11
OP_CAST = 12
OP_NAMES = ["LOAD", "LOADV", "STORE", "ARITHETIC", "LOGIC", "LABEL", "JUMP", "JUMP_ZERO", "COMPLEMENT", "SHIFT", "CALL", "RETURN", "CAST"]


class PseudoOp:
    def __init__(self, kind: int, *args, data_type: DataType = None):
        self.kind = kind
        self.size = data_type.size if data_type is not None else 0
        self.args = args

    def __repr__(self):
        return f"{OP_NAMES[self.kind]} ({self.size}): {self.args}"


class PseudoState:
    def __init__(self, scope: Scope, func: Function):
        self.ops: List[PseudoOp] = []
        self._reg_count = 0
        self._free_regs = []
        self._label_nr = 0
        self._func = func
        self._scope = scope
        self.block(func.block)
        assert len(self._free_regs) == self._reg_count, f"{self._free_regs} != {self._reg_count}"

    def block(self, block):
        for node in block:
            r = self.step(node, None)
            if r != -1:
                self.free_reg(r)

    def new_reg(self):
        self._reg_count += 1
        return self._reg_count

    def free_reg(self, r):
        assert r > 0
        self._free_regs.append(r)

    def step(self, node: AstNode, data_type: DataType):
        r0 = -1
        if node.kind == '=':
            assert data_type is None
            label, data_type = self._scope.resolve_var(node.params[0])
            r1 = self.step(node.params[1], data_type)
            self.ops.append(PseudoOp(OP_STORE, r1, label, data_type=data_type))
            self.free_reg(r1)
        elif node.kind == 'VAR':
            assert data_type is None
            label, data_type = self._scope.resolve_var(node)
            r1 = self.step(node.params[0], data_type)
            self.ops.append(PseudoOp(OP_STORE, r1, label, data_type=data_type))
            self.free_reg(r1)
        elif node.kind == 'RETURN':
            if node.params:
                r1 = self.step(node.params[0], self._func.return_type)
                self.ops.append(PseudoOp(OP_STORE, r1, "_result__", data_type=self._func.return_type))
                self.free_reg(r1)
            self.ops.append(PseudoOp(OP_RETURN))
        elif node.kind in {'U-'}:
            r0 = self.step(node.params[0], data_type)
            self.ops.append(PseudoOp(OP_COMPLEMENT, r0, data_type=data_type))
        elif node.kind in {'+', '-', '*', '/', '%', '&', '|', '^'}:
            r0 = self.step(node.params[0], data_type)
            r1 = self.step(node.params[1], data_type)
            self.ops.append(PseudoOp(OP_ARITHMETIC, node.kind, r0, r1, data_type=data_type))
            self.free_reg(r1)
        elif node.kind in {'<', '>', '==', '!='}:
            r0 = self.step(node.params[0], data_type)
            r1 = self.step(node.params[1], data_type)
            self.ops.append(PseudoOp(OP_LOGIC, node.token.value, r0, r1, data_type=data_type))
            self.free_reg(r1)
        elif node.kind == 'SHIFT':
            r0 = self.step(node.params[0], data_type)
            r1 = self.step(node.params[1], data_type)
            self.ops.append(PseudoOp(OP_SHIFT, node.token.value, r0, r1, data_type=data_type))
            self.free_reg(r1)
        elif node.kind == 'ID':
            label, var_data_type = self._scope.resolve_var(node)
            if var_data_type != data_type:
                raise CompileException(node.token, f"Wrong type {var_data_type} != {data_type}")
            r0 = self.new_reg()
            self.ops.append(PseudoOp(OP_LOAD, r0, label, data_type=data_type))
        elif node.kind == 'NUM':
            r0 = self.new_reg()
            self.ops.append(PseudoOp(OP_LOAD_VALUE, r0, node.token.value, data_type=data_type))
        elif node.kind == 'CAST':
            if node.params[1].data_type != data_type:
                raise CompileException(node.token, f"Wrong type {var_data_type} != {data_type}")
            source_type = self.discover_type(node.params[0])
            r0 = self.step(node.params[0], source_type)
            self.ops.append(PseudoOp(OP_CAST, r0, data_type.size, data_type=source_type))
        elif node.kind == 'IF':
            r1 = self.step(node.params[0], DEFAULT_TYPE)
            if_label = self.next_label()
            self.ops.append(PseudoOp(OP_JUMP_ZERO, if_label, r1, data_type=DEFAULT_TYPE))
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
        elif node.kind == 'WHILE':
            check_label = self.next_label()
            end_label = self.next_label()
            self.ops.append(PseudoOp(OP_LABEL, check_label))
            r1 = self.step(node.params[0], DEFAULT_TYPE)
            self.ops.append(PseudoOp(OP_JUMP_ZERO, end_label, r1, data_type=DEFAULT_TYPE))
            self.free_reg(r1)
            self.block(node.params[1:])
            self.ops.append(PseudoOp(OP_JUMP, check_label))
            self.ops.append(PseudoOp(OP_LABEL, end_label))
        elif node.kind == 'CALL':
            func = self._scope.find_function(node.params[0])
            if len(func.parameters) != len(node.params) - 1:
                raise CompileException(node.token, f"Wrong number of parameters to function {func.name}")
            if data_type is not None and data_type != func.return_type:
                raise CompileException(node.token, f"Type mismatch {data_type} != {func.return_type}")
            for param_node, param in zip(node.params[1:], func.parameters):
                r1 = self.step(param_node, param.data_type)
                self.ops.append(PseudoOp(OP_STORE, r1, f"local_{func.name}_{param.token.value}", data_type=param.data_type))
                self.free_reg(r1)
            self.ops.append(PseudoOp(OP_CALL, func.name))
            if data_type:
                r0 = self.new_reg()
                self.ops.append(PseudoOp(OP_LOAD, r0, "_result__", data_type=data_type))
        else:
            raise CompileException(node.token, f"Do not know how to convert {node} into pseudo ops")
        return r0

    def discover_type(self, node: AstNode):
        if node.data_type:
            return node.data_type
        if node.kind == "ID":
            return self._scope.resolve_var(node)[1]
        for p in node.params:
            res = self.discover_type(p)
            if res:
                return res
        return None

    def next_label(self):
        self._label_nr += 1
        return self._label_nr
