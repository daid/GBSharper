from typing import Dict, Optional, Callable, Union, Tuple, List
from ..scanner import Scanner
from ..astnode import AstNode
from ..exception import CompileException
from .datatype import parse_datatype


PREC_NONE = 0
PREC_ASSIGNMENT = 1   # =
PREC_LOGIC_OR = 2     # or
PREC_LOGIC_AND = 3    # and
PREC_BITWISE_OR = 4   # |
PREC_BITWISE_XOR = 5  # ^
PREC_BITWISE_AND = 6  # &
PREC_EQUALITY = 7     # == !=
PREC_COMPARISON = 8   # < > <= >=
PREC_SHIFT = 9        # << >>
PREC_TERM = 10        # + -
PREC_FACTOR = 11      # * /
PREC_UNARY = 12       # ! -
PREC_CALL = 13        # . () []
PREC_PRIMARY = 14

PrefixRuleFunction = Callable[[Scanner], AstNode]
InfixRuleFunction = Callable[[Scanner], Tuple[str, Union[AstNode, List[AstNode]]]]


class Rule:
    def __init__(self, prefix: Optional[PrefixRuleFunction], infix: Optional[InfixRuleFunction], precedence: int):
        self.prefix = prefix
        self.infix = infix
        self.precedence = precedence


rules: Dict[str, Rule] = {}


def value(scanner: Scanner) -> AstNode:
    scanner.advance()
    return AstNode(scanner.previous.kind, scanner.previous)


def grouping(scanner: Scanner) -> AstNode:
    scanner.advance()
    res = expression(scanner)
    scanner.consume(')')
    return res


def unary(scanner: Scanner) -> AstNode:
    scanner.advance()
    t = scanner.previous
    return AstNode(f"U{t.kind}", t, parse_precedence(scanner, PREC_UNARY))


def index(scanner: Scanner) -> Tuple[str, AstNode]:
    t = scanner.previous
    res = expression(scanner)
    scanner.consume(']')
    return t.kind, res


def call(scanner: Scanner) -> Tuple[str, List[AstNode]]:
    if scanner.current.kind == ')':
        scanner.consume(')')
        return "CALL", []
    params = [expression(scanner)]
    while scanner.current.kind == ',':
        scanner.consume(',')
        params.append(expression(scanner))
    scanner.consume(')')
    return 'CALL', params


def binary(scanner: Scanner) -> Tuple[str, AstNode]:
    t = scanner.previous
    rule = rules[t.kind]
    res = parse_precedence(scanner, rule.precedence + 1)
    return t.kind, res


def binary_cast(scanner: Scanner) -> Tuple[str, AstNode]:
    t = scanner.previous
    return "CAST", AstNode(t.kind, t, data_type=parse_datatype(scanner))


def parse_precedence(scanner: Scanner, precedence: int) -> AstNode:
    if scanner.current.kind not in rules:
        raise CompileException(scanner.current, f"Unexpected {scanner.current.kind}")
    prefix_rule = rules[scanner.current.kind].prefix
    if prefix_rule is None:
        raise CompileException(scanner.current, "Expect expression.")
    a = prefix_rule(scanner)

    while scanner.current.kind in rules and precedence <= rules[scanner.current.kind].precedence:
        scanner.advance()
        t = scanner.previous
        infix_rule = rules[t.kind].infix
        assert infix_rule is not None
        b, c = infix_rule(scanner)
        if isinstance(c, list):
            a = AstNode(b, t, a, *c)
        else:
            a = AstNode(b, t, a, c)
    return a


def expression(scanner: Scanner) -> AstNode:
    if scanner.check('{'):
        first_token = scanner.current
        params = [expression(scanner)]
        while scanner.check(','):
            params.append(expression(scanner))
        scanner.consume('}')
        return AstNode("ARRAY", first_token, *params)
    return parse_precedence(scanner, PREC_ASSIGNMENT)


rules['ID'] = Rule(value, None, PREC_NONE)
rules['STRING'] = Rule(value, None, PREC_NONE)
rules['&'] = Rule(unary, binary, PREC_BITWISE_AND)
rules['^'] = Rule(None, binary, PREC_BITWISE_XOR)
rules['|'] = Rule(None, binary, PREC_BITWISE_OR)
rules['+'] = Rule(None, binary, PREC_TERM)
rules['!'] = Rule(unary, None, PREC_TERM)
rules['-'] = Rule(unary, binary, PREC_TERM)
rules['/'] = Rule(None, binary, PREC_FACTOR)
rules['*'] = Rule(unary, binary, PREC_FACTOR)
rules['%'] = Rule(None, binary, PREC_FACTOR)
rules['SHIFT'] = Rule(None, binary, PREC_SHIFT)
rules['=='] = Rule(None, binary, PREC_EQUALITY)
rules['AS'] = Rule(None, binary_cast, PREC_COMPARISON)
rules['<'] = Rule(None, binary, PREC_COMPARISON)
rules['>'] = Rule(None, binary, PREC_COMPARISON)
rules['<='] = Rule(None, binary, PREC_COMPARISON)
rules['>='] = Rule(None, binary, PREC_COMPARISON)
rules['&&'] = Rule(None, binary, PREC_LOGIC_AND)
rules['||'] = Rule(None, binary, PREC_LOGIC_OR)
rules['NUM'] = Rule(value, None, PREC_NONE)
rules['.'] = Rule(None, binary, PREC_CALL)
rules['='] = Rule(None, binary, PREC_ASSIGNMENT)
rules['['] = Rule(None, index, PREC_CALL)
rules['('] = Rule(grouping, call, PREC_CALL)


def main() -> None:
    scanner = Scanner("[main]", "a.b[1] += f(1 + 3 / (4 * 5), -2)")
    ast = expression(scanner)
    ast.dump()
    print(ast)


if __name__ == "__main__":
    main()
