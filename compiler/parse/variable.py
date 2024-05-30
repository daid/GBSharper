from ..exception import CompileException
from ..scanner import Scanner
from ..astnode import AstNode
from .expression import expression
from ..datatype import DEFAULT_TYPE
from .datatype import parse_datatype


def parse_var(scanner: Scanner) -> AstNode:
    scanner.consume('ID')
    name_token = scanner.previous
    data_type = DEFAULT_TYPE
    if scanner.check(':', ':'):
        data_type = parse_datatype(scanner)
    if scanner.check('=', '='):
        value = expression(scanner)
        return AstNode("VAR", name_token, value, data_type=data_type)
    else:
        raise CompileException(scanner.current, f"Unexpected: {scanner.current.value}")
