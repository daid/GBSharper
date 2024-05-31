from typing import Dict, Optional
from .astnode import AstNode
from .parse.function import Function
from .exception import CompileException


class Scope:
    def __init__(self, prefix: str, parent: Optional["Scope"]):
        self.prefix = prefix
        self.vars: Dict[str, AstNode] = {}
        self.parent = parent

    def resolve_var_name(self, node: AstNode):
        if node.token.value in self.vars:
            return f"{self.prefix}_{node.token.value}"
        if self.parent:
            return self.parent.resolve_var_name(node)
        raise CompileException(node.token, f"Variable not found: {node.token.value}")

    def find_function(self, node: AstNode):
        return self.parent.find_function(node)


class TopLevelScope(Scope):
    def __init__(self, prefix: str):
        super().__init__(prefix, None)
        self.funcs: Dict[str, Function] = {}
        self.regs: Dict[str, int] = {}

    def resolve_var_name(self, node: AstNode):
        if node.token.value in self.regs:
            return node.token.value
        return super().resolve_var_name(node)

    def find_function(self, node: AstNode):
        if node.token.value in self.funcs:
            return self.funcs[node.token.value]
        raise CompileException(node.token, f"Function not found: {node.token.value}")
