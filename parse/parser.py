from parse.function import parse_function
from parse.variable import parse_var
from scanner import Scanner
from module import Module


def parse(module_name: str, code: str) -> Module:
    module = Module(module_name)
    scanner = Scanner(module_name, code)
    while scanner:
        if scanner.check('ID', 'var'):
            module.vars.append(parse_var(scanner))
        elif scanner.check('ID', 'const'):
            module.consts.append(parse_var(scanner))
        elif scanner.check('ID', 'fn'):
            module.funcs.append(parse_function(scanner))

        if scanner and not scanner.current.kind == "NEWLINE":
            scanner.error(f"Unexpected: {scanner.current.value}")
        while scanner and not scanner.current.kind == "NEWLINE":
            scanner.advance()
        if scanner and scanner.current.value != 0:
            scanner.error(f"Unexpected indentation")
        scanner.advance()
    return module
