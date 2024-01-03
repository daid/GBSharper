from typing import List

from astnode import AstNode
from parse.function import Function


class Module:
    def __init__(self, name: str):
        self.name = name
        self.vars: List[AstNode] = []
        self.consts: List[AstNode] = []
        self.funcs: List[Function] = []

    def dump(self):
        print(f"Module: {self.name}")
        for idx, var in enumerate(self.vars):
            var.dump(last=idx == len(self.vars)-1)
        for idx, func in enumerate(self.funcs):
            func.dump(last=idx == len(self.funcs)-1)
