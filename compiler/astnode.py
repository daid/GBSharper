from .scanner import Token


class AstNode:
    __slots__ = ("kind", "token", "params", "data_type")

    def __init__(self, kind: str, token: Token, *params: "AstNode", data_type=None):
        self.kind = kind
        self.token = token
        self.params = params
        self.data_type = data_type

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
        dt = ""
        if self.data_type:
            dt = f" {self.data_type}"
        if len(self.params) == 0:
            return f"{self.kind}<{self.token.value}>{dt}"
        return f"{self.kind}{self.params}{dt}"
