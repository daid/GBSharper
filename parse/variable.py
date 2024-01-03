from exception import CompileException
from scanner import Scanner
from astnode import AstNode
from .expression import expression


def parse_var(scanner: Scanner) -> AstNode:
    scanner.consume('ID')
    name_token = scanner.previous
    if scanner.check('=', '='):
        value = expression(scanner)
        return AstNode("VAR", name_token, value)
    else:
        raise CompileException(scanner.current, f"Unexpected: {scanner.current.value}")
