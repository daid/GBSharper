from .scanner import Token


class AstNode:
    __slots__ = ("kind", "token", "params")

    def __init__(self, kind: str, token: Token, *params: "AstNode"):
        self.kind = kind
        self.token = token
        self.params = params

    def dump(self, indent: str = "", last: bool = True) -> None:
        print(f"{indent}{'`' if last else '|'}-:{self.kind} {self.token}")
        indent += "  " if last else "| "
        for idx, param in enumerate(self.params):
            param_last = idx == len(self.params) - 1
            if isinstance(param, AstNode):
                param.dump(indent, param_last)
            else:
                print(f"{indent}{'`' if param_last else '|'}-{param}")

    def __repr__(self) -> str:
        if len(self.params) == 0:
            return f"{self.kind}<{self.token.value}>"
        return f"{self.kind}{self.params}"
