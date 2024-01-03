from scanner import Scanner, Token
from astnode import AstNode
from .expression import expression
from typing import List


def parse_block(scanner: Scanner, minimal_indent: int = 1) -> List[AstNode]:
    result: List[AstNode] = []
    scanner.consume("NEWLINE")
    indent_level = int(scanner.previous.value)
    if indent_level < minimal_indent:
        scanner.error("Expected indent block")
    while True:
        # if scanner.check('ID', 'var'):
        #     result.append(parse_var(scanner))
        if scanner.check('ID', 'return'):
            token = scanner.previous
            if scanner.current.kind == "NEWLINE" or scanner.current.kind == "":
                result.append(AstNode("RETURN", token))
            else:
                result.append(AstNode("RETURN", token, expression(scanner)))
        elif scanner.check('ID', 'if'):
            if_token = scanner.previous
            condition = expression(scanner)
            block = parse_block(scanner, indent_level + 1)
            result.append(AstNode("IF", if_token, condition, AstNode("TRUE", scanner.current, *block)))
        elif scanner.check('ID', 'elif'):
            if result[-1].kind != "IF":
                scanner.error("Unexpected elif")
            if_token = scanner.previous
            condition = expression(scanner)
            block = parse_block(scanner, indent_level + 1)
            result[-1].params = (*result[-1].params, condition, AstNode("ELIF", if_token, *block))
        elif scanner.check('ID', 'else'):
            if result[-1].kind != "IF":
                scanner.error("Unexpected else")
            block = parse_block(scanner, indent_level + 1)
            result[-1].params = (*result[-1].params, AstNode("FALSE", scanner.current, *block))
        elif scanner.check('ID', 'while'):
            while_token = scanner.previous
            condition = expression(scanner)
            block = parse_block(scanner, indent_level + 1)
            result.append(AstNode("WHILE", while_token, condition, *block))
        else:
            result.append(expression(scanner))
        if not scanner.check('NEWLINE', indent_level):
            if scanner.current.kind == 'NEWLINE' and int(scanner.current.value) > indent_level:
                scanner.error("Unexpected indent")
            break
    return result
