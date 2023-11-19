from typing import List, Dict, Any, Union

from gumtree.tree.abstract_tree import EmptyEntryIterator, AbstractTree
from gumtree.tree.type import Type


class UnsupportedOperationException(Exception):
    pass


class FakeTree(AbstractTree):

    def __init__(self, *trees: 'Tree'):
        super().__init__()
        if trees and trees[0] is not None:
            self.children = list(trees)
        else:
            self.children = []

    def unsupported_operation(self):
        raise UnsupportedOperationException("This method should not be called on a fake tree")

    def deep_copy(self) -> 'Tree':
        copy = FakeTree()
        for child in self.get_children():
            copy.add_child(child.deep_copy())
        return copy

    def get_label(self) -> str:
        return self.NO_LABEL

    def get_length(self) -> int:
        return self.get_end_pos() - self.get_pos()

    def get_pos(self) -> int:
        return min(self.children, key=lambda t: t.get_pos()).get_pos()

    def get_end_pos(self) -> int:
        return max(self.children, key=lambda t: t.get_pos()).get_end_pos()

    def get_type(self) -> Type:
        return Type.NO_TYPE

    def set_label(self, label: str):
        self.unsupported_operation()

    def set_length(self, length: int):
        self.unsupported_operation()

    def set_pos(self, pos: int):
        self.unsupported_operation()

    def set_type(self, type: Type):
        self.unsupported_operation()

    def __str__(self) -> str:
        return "FakeTree"

    def get_metadata(self, key: str) -> Any:
        return None

    def set_metadata(self, key: str, value: Any) -> Any:
        self.unsupported_operation()

    def get_all_metadata(self) -> 'EmptyEntryIterator':
        return EmptyEntryIterator()

