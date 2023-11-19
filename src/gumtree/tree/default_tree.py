from typing import List, Dict, Iterator, Tuple, Union, Optional

from gumtree.tree.abstract_tree import AbstractTree
from gumtree.tree.tree import Tree
from gumtree.tree.type import Type


class DefaultTree(AbstractTree, Tree):  # Assuming you have AbstractTree defined from previous conversions

    def __init__(self, tree_type: Type, label: str = Tree.NO_LABEL):
        super().__init__()
        self.type = tree_type
        self.label = label or self.NO_LABEL
        self.children = []
        self.pos = 0
        self.length = 0
        self.metadata = None

    def deep_copy(self) -> 'DefaultTree':
        copy = DefaultTree(self.type, self.label)
        copy.ast = self.ast
        for child in self.children:
            copy.add_child(child.deep_copy())
        return copy

    def get_label(self) -> str:
        return self.label

    def get_length(self) -> int:
        return self.length

    def get_pos(self) -> int:
        return self.pos

    def get_type(self) -> Type:
        return self.type

    def set_label(self, label: str):
        self.label = label or self.NO_LABEL

    def set_length(self, length: int):
        self.length = length

    def set_pos(self, pos: int):
        self.pos = pos

    def set_type(self, tree_type: Type):
        self.type = tree_type

    def get_metadata(self, key: str) -> Optional[object]:
        if not self.metadata:
            return None
        return self.metadata.get(key)

    def set_metadata(self, key: str, value: object) -> object:
        if value is None:
            return self.metadata and self.metadata.pop(key, None)
        if not self.metadata:
            self.metadata = {}
        return self.metadata.setdefault(key, value)

    def get_all_metadata(self) -> Iterator[Tuple[str, object]]:
        return iter(self.metadata.items()) if self.metadata else iter([])
