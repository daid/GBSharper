from ..astnode import AstNode
from typing import Dict


def constant_collapse(node: AstNode, lookup: Dict[str, int]={}):
    for p in node.params:
        constant_collapse(p, lookup)
    if node.kind in {'+', '-', '/', '*', 'SHIFT'} and node.params[0].kind == "NUM" and node.params[1].kind == "NUM":
        if node.kind == '+':
            node.token.value = node.params[0].token.value + node.params[1].token.value
        elif node.kind == '-':
            node.token.value = node.params[0].token.value - node.params[1].token.value
        elif node.kind == '/':
            node.token.value = node.params[0].token.value // node.params[1].token.value
        elif node.kind == '*':
            node.token.value = node.params[0].token.value * node.params[1].token.value
        elif node.kind == 'SHIFT' and node.token.value == '<<':
            node.token.value = node.params[0].token.value << node.params[1].token.value
        elif node.kind == 'SHIFT' and node.token.value == '>>':
            node.token.value = node.params[0].token.value >> node.params[1].token.value
        else:
            raise RuntimeError(node.kind)
        node.kind = node.params[0].kind
        node.params = ()
    elif node.kind == 'U-' and node.params[0].kind == "NUM":
        node.token.value = -node.params[0].token.value
        node.kind = node.params[0].kind
        node.params = ()
    elif node.kind == "ID" and node.token.value in lookup:
        node.kind = "NUM"
        node.token.value = lookup[node.token.value]
