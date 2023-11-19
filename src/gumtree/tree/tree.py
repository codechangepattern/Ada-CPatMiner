import re
from typing import Iterable, List, Tuple, Dict, Optional, Union, Iterator

from gumtree.tree.tree_metrics import TreeMetrics
from gumtree.tree.tree_utils import TreeUtils
from gumtree.tree.type import Type


class Tree:
    url_pattern = re.compile(r"\d+(\.\d+)*")
    NO_LABEL = ""
    NO_POS = -1

    def pre_order(self) -> Iterable['Tree']:
        return TreeUtils.pre_order_iterator(self)

    def post_order(self) -> Iterable['Tree']:
        return TreeUtils.post_order_iterator(self)

    def breadth_first(self) -> Iterable['Tree']:
        return TreeUtils.breadth_first_iterator(self)

    def add_child(self, t: 'Tree'):
        raise NotImplementedError

    def insert_child(self, t: 'Tree', position: int):
        raise NotImplementedError

    def set_children(self, children: List['Tree']):
        raise NotImplementedError

    def get_child_position(self, child: 'Tree') -> int:
        return self.get_children().index(child)

    def get_child(self, position: int) -> 'Tree':
        return self.get_children()[position]

    def get_trees_between_positions(self, position: int, end_position: int) -> List['Tree']:
        trees = [t for t in self.pre_order() if t.get_pos() >= position and t.get_end_pos() <= end_position]
        return trees

    def get_child_by_url(self, url: str) -> 'Tree':
        if not self.url_pattern.match(url):
            raise ValueError(f"Wrong URL format: {url}")

        path = url.split(".")
        current = self
        while path:
            next_idx = int(path.pop(0))
            current = current.get_child(next_idx)

        return current

    def get_children(self) -> List['Tree']:
        raise NotImplementedError

    def is_leaf(self) -> bool:
        return not bool(self.get_children())

    def search_subtree(self, subtree: 'Tree') -> List['Tree']:
        return [candidate for candidate in self.pre_order() if candidate.get_metrics().hash == subtree.get_metrics().hash and candidate.is_isomorphic_to(subtree)]

    def get_descendants(self) -> List['Tree']:
        return TreeUtils.pre_order(self)[1:]

    def set_parent(self, parent: 'Tree'):
        raise NotImplementedError

    def set_parent_and_update_children(self, parent: 'Tree'):
        raise NotImplementedError

    def is_root(self) -> bool:
        return self.get_parent() is None

    def get_parent(self) -> Optional['Tree']:
        raise NotImplementedError

    def get_parents(self) -> List['Tree']:
        parents = []
        if self.get_parent():
            parents.append(self.get_parent())
            parents.extend(self.get_parent().get_parents())
        return parents

    def position_in_parent(self) -> int:
        parent = self.get_parent()
        if parent is None:
            return -1
        else:
            return parent.get_children().index(self)

    def deep_copy(self) -> 'Tree':
        raise NotImplementedError

    def has_label(self) -> bool:
        return self.get_label() != self.NO_LABEL

    def get_label(self) -> str:
        raise NotImplementedError

    def set_label(self, label: str):
        raise NotImplementedError

    def get_pos(self) -> int:
        raise NotImplementedError

    def set_pos(self, pos: int):
        raise NotImplementedError

    def get_length(self) -> int:
        raise NotImplementedError

    def set_length(self, length: int):
        raise NotImplementedError

    def get_end_pos(self) -> int:
        return self.get_pos() + self.get_length()

    def get_type(self) -> Type:
        raise NotImplementedError

    def set_type(self, type: Type):
        raise NotImplementedError

    def has_same_type(self, t: 'Tree') -> bool:
        return self.get_type() == t.get_type()

    def has_same_type_and_label(self, t: 'Tree') -> bool:
        return self.has_same_type(t) and self.get_label() == t.get_label()

    def is_isomorphic_to(self, tree: 'Tree') -> bool:
        if not self.has_same_type_and_label(tree):
            return False

        if len(self.get_children()) != len(tree.get_children()):
            return False

        for i in range(len(self.get_children())):
            if not self.get_child(i).is_isomorphic_to(tree.get_child(i)):
                return False

        return True

    def is_iso_structural_to(self, tree: 'Tree') -> bool:
        if self.get_type() != tree.get_type():
            return False

        if len(self.get_children()) != len(tree.get_children()):
            return False

        for i in range(len(self.get_children())):
            if not self.get_child(i).is_iso_structural_to(tree.get_child(i)):
                return False

        return True

    def to_tree_string(self) -> str:
        raise NotImplementedError

    def get_metrics(self) -> TreeMetrics:
        raise NotImplementedError

    def set_metrics(self, metrics: TreeMetrics):
        raise NotImplementedError

    def get_metadata(self, key: str) -> Union[object, Iterator[Tuple[str, object]]]:
        raise NotImplementedError

    def set_metadata(self, key: str, value: object) -> object:
        raise NotImplementedError

