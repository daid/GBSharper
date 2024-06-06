from ..scanner import Scanner
from ..datatype import DataType, BASE_TYPES
from ..exception import CompileException


def parse_datatype(scanner: Scanner):
    scanner.consume('ID')
    if scanner.previous.value not in BASE_TYPES:
        raise CompileException(scanner.current, f"Unexpected: {scanner.current.value}")
    datatype = BASE_TYPES[scanner.previous.value]
    while scanner.check('*'):
        print("OHHO!")
    return datatype