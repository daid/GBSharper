from typing import List, Optional
from ..astnode import AstNode
from ..scanner import Scanner, Token
from .block import parse_block
from ..datatype import DEFAULT_TYPE


class Parameter:
    def __init__(self, name: str, vartype: AstNode):
        self.name = name
        self.vartype = vartype

    def __repr__(self) -> str:
        return f"{self.name}: {self.vartype}"


class Function(AstNode):
    def __init__(self, token: Token):
        super().__init__("FUNC", token)
        self.name = str(token.value)
        self.parameters: List[Parameter] = []
        self.return_type: Optional[AstNode] = None
        self.block: List[AstNode] = []
        self.__typename = ""

    def dump(self, indent: str = "", last: bool = True) -> None:
        print(f"{indent}{'`' if last else '|'}-:{self.kind} {self.token} {self.parameters}")
        indent += "  " if last else "| "
        for idx, block in enumerate(self.block):
            block.dump(indent, idx == len(self.block) - 1)


def parse_function(scanner: Scanner):
    scanner.consume('ID')
    function = Function(scanner.previous)
    while scanner.check("ID"):
        var_name = scanner.previous.value
        function.parameters.append(Parameter(var_name, DEFAULT_TYPE))
    # TODO return value
    function.block = parse_block(scanner)
    return function
