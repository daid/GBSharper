from typing import Dict, Optional, Tuple
from .astnode import AstNode
from .parse.function import Function
from .exception import CompileException
from .datatype import DataType


class Scope:
    def __init__(self, prefix: str, parent: Optional["Scope"]):
        self.prefix = prefix
        self.vars: Dict[str, AstNode] = {}
        self.parent = parent

    def resolve_var(self, node: AstNode) -> Tuple[str, DataType]:
        if node.token.value in self.vars:
            return f"{self.prefix}_{node.token.value}", self.vars[node.token.value].data_type
        if self.parent:
            return self.parent.resolve_var(node)
        raise CompileException(node.token, f"Variable not found: {node.token.value}")

    def find_function(self, node: AstNode):
        return self.parent.find_function(node)


class TopLevelScope(Scope):
    def __init__(self, prefix: str):
        super().__init__(prefix, None)
        self.funcs: Dict[str, Function] = {}
        self.regs: Dict[str, AstNode] = {}

    def resolve_var(self, node: AstNode) -> Tuple[str, DataType]:
        if node.token.value in self.regs:
            return node.token.value, self.regs[node.token.value].data_type
        return super().resolve_var(node)

    def find_function(self, node: AstNode):
        if node.token.value in self.funcs:
            return self.funcs[node.token.value]
        raise CompileException(node.token, f"Function not found: {node.token.value}")
