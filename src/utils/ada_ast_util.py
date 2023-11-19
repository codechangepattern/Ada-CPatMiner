from typing import Type

from libadalang import AdaNode, _kind_to_astnode_cls, BinOp
from multimethod import multimethod


@multimethod
def is_literal(ast_node_type: int) -> bool:
    return _kind_to_astnode_cls[ast_node_type].__name__.endswith('Literal')


@multimethod
def is_literal(node: AdaNode) -> bool:
    return node.__class__.__name__.endswith('Literal')


@multimethod
def node_type(node_class: Type[object]) -> int:
    return list(_kind_to_astnode_cls.keys())[list(_kind_to_astnode_cls.values()).index(node_class)]


@multimethod
def node_type(node: AdaNode) -> int:
    return node_type(node.__class__)


def start_position(node: AdaNode) -> int:
    lines: list[str] = node.unit.root.text.splitlines()
    position: int = 0
    for i in range(0, node.sloc_range.start.line - 1):
        position += len(lines[i])
    position += node.sloc_range.start.column
    return position
