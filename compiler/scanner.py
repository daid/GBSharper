from typing import Optional, Union
from .exception import CompileException


class Token:
    __slots__ = ("kind", "value", "line_number", "module")

    def __init__(self, kind: str, value: Union[str, int], line_number: int, module: str):
        self.kind = kind
        self.value = value
        self.line_number = line_number
        self.module = module

    def __repr__(self) -> str:
        if self.kind != self.value:
            return f"<{self.kind}:{self.value}>"
        return f"<{self.kind}>"


class Scanner:
    OPS = {
        "SHIFT": {"<<", ">>"},
        "==": {"<=", ">=", "==", "!="},
        "&&": {"&&"},
        "||": {"||"},
        "=": {"+=", "-=", "*=", "/=", "%=", "<<=", ">>=", "&=", "^=", "|="},
    }

    def __init__(self, module_name: str, code: str):
        self.OP_LOOKUP = {}
        for group, ops in self.OPS.items():
            for op in ops:
                self.OP_LOOKUP[op] = group
        self.__code = code
        self.__position = 0
        self.__line_number = 1
        self.__module = module_name
        self.previous = Token("", "", -1, module_name)
        self.current = Token("", "", -1, module_name)
        self.advance()

    def advance(self) -> None:
        self.previous = self.current
        while self.__next() in {" ", "\t"}:
            self.__position += 1
        if self.__position >= len(self.__code):
            self.current = Token("", "", self.__line_number, self.__module)
            return
        c = self.__code[self.__position]
        if c == ';' or c == '#':
            while self.__position < len(self.__code) and self.__next() != "\n":
                self.__position += 1
            self.advance()
            return
        self.__position += 1
        if c in "0123456789":
            base = 10
            if self.__next().lower() == "x":
                self.__position += 1
                base = 16
                while self.__next() in {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "a", "b", "c", "d", "e", "f"}:
                    c += self.__code[self.__position]
                    self.__position += 1
            elif self.__next().lower() == "b":
                self.__position += 1
                base = 2
                while self.__next() in {"0", "1"}:
                    c += self.__code[self.__position]
                    self.__position += 1
            else:
                while self.__next() in {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"}:
                    c += self.__code[self.__position]
                    self.__position += 1
            self.current = Token("NUM", int(c, base), self.__line_number, self.__module)
        elif c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_":
            while self.__next() in {"A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "_", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"}:
                c += self.__code[self.__position]
                self.__position += 1
            self.current = Token("ID", c, self.__line_number, self.__module)
        elif c == "\n" or c == "\r":
            if c == "\r" and self.__next() == "\n":
                self.__position += 1
            indent = 0
            while self.__next() == " ":
                self.__position += 1
                indent += 1
            if self.__next() == ";":   # skip empty lines with just comments
                while self.__next() not in {"", "\n"}:
                    self.__position += 1
            if self.__next() == "\n":  # skip empty lines in the tokenizer.
                self.__line_number += 1
                return self.advance()
            if self.__next() == "":  # End of file
                return self.advance()
            self.__line_number += 1
            self.current = Token("NEWLINE", indent, self.__line_number, self.__module)
        elif c == '"':
            value = ""
            while True:
                c = self.__next()
                self.__position += 1
                if c in {"\"", ""}:
                    break
                if c == '\\':
                    c = self.__next()
                    self.__position += 1
                    if c.lower() == 'x':
                        upper_nibble = self.__next()
                        self.__position += 1
                        lower_nibble = self.__next()
                        self.__position += 1
                        try:
                            value += chr(int(upper_nibble + lower_nibble, 16))
                        except ValueError:
                            raise CompileException(self.current, "String format error")
                    else:
                        value += c
                else:
                    value += c
            self.current = Token("STRING", value, self.__line_number, self.__module)
        elif c + self.__next() in self.OP_LOOKUP:
            c += self.__code[self.__position]
            self.__position += 1
            self.current = Token(self.OP_LOOKUP[c], c, self.__line_number, self.__module)
        else:
            self.current = Token(c, c, self.__line_number, self.__module)

    def __next(self) -> str:
        if self.__position < len(self.__code):
            return self.__code[self.__position]
        return ""

    def check(self, kind: str, value: Optional[Union[str, int]] = None) -> bool:
        if self.current.kind == kind and (value is None or self.current.value == value):
            self.advance()
            return True
        return False

    def consume(self, kind: str) -> None:
        if self.current.kind != kind:
            raise CompileException(self.current, f"Syntax error, unexpected: {self.current.kind}, expected: {kind}")
        self.advance()

    def error(self, message: str) -> None:
        raise CompileException(self.current, message)

    def __bool__(self) -> bool:
        return self.current.kind != ""
