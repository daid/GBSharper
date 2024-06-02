from typing import List, Optional
from ..astnode import AstNode
from ..scanner import Scanner, Token
from ..datatype import DEFAULT_TYPE, DataType
from .block import parse_block
from .datatype import parse_datatype


class Function(AstNode):
    def __init__(self, token: Token):
        super().__init__("FUNC", token)
        self.name = str(token.value)
        self.parameters: List[AstNode] = []
        self.vars: List[AstNode] = []
        self.return_type: Optional[DataType] = None
        self.block: List[AstNode] = []

    def set_block(self, block: List[AstNode]):
        if not block or block[-1].kind != "RETURN":
            block.append(AstNode("RETURN", None))
        self.block = block
        for node in block:
            self._find_vars(node)
    
    def _find_vars(self, node: AstNode):
        for child in node.params:
            self._find_vars(child)
        if node.kind == "VAR":
            self.vars.append(node)

    def dump(self, indent: str = "", last: bool = True) -> None:
        print(f"{indent}{'`' if last else '|'}-:{self.kind} {self.token} {self.parameters}")
        indent += "  " if last else "| "
        for idx, block in enumerate(self.block):
            block.dump(indent, idx == len(self.block) - 1)


def parse_function(scanner: Scanner):
    scanner.consume('ID')
    function = Function(scanner.previous)
    while scanner.check("ID"):
        data_type = DEFAULT_TYPE
        if scanner.check(':', ':'):
            data_type = parse_datatype(scanner)
        function.parameters.append(AstNode("PARAM", scanner.previous, data_type=data_type))
    if scanner.check(">"):
        function.return_type = parse_datatype(scanner)
    function.set_block(parse_block(scanner))
    return function
