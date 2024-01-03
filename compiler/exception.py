from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scanner import Token


class CompileException(Exception):
    def __init__(self, token: "Token", message: str):
        self.message = message
        self.token = token

    def __str__(self) -> str:
        return f"{self.message} @ {self.token.module}:{self.token.line_number}"
