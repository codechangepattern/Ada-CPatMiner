from __future__ import annotations

from bisect import insort
from functools import cmp_to_key
from typing import Optional, cast

import libadalang as lal

from libadalang import AdaNode, Identifier, Expr, _kind_to_astnode_cls, BinOp, SubpBody, Stmt, BlockStmt, ReturnStmt, \
    ExitStmt, ForLoopStmt, WhileLoopStmt, ObjectDecl, DefiningNameList, DefiningName
from multimethod import multimethod
from overrides import overrides

from utils.ada_node_matcher import match
from utils.ada_node_visitor import AdaNodeVisitor, accept
from utils.pair import Pair
from utils.string_processor import compute_char_lcs, serialize_to_chars
from log import logger


class TreedConstants:
    GRAM_MAX_LENGTH: int = 2
    MIN_HEIGHT: int = 2
    MIN_SIMILARITY: float = 0.5
    MIN_SIMILARITY_MOVE: float = 0.75
    SIMILARITY_SMOOTH: float = (3 * MIN_SIMILARITY - 1) / (1 - MIN_SIMILARITY)

    STATUS_UNCHANGED: int = 0
    STATUS_RELABELED: int = 1
    STATUS_UNMAPPED: int = 2
    STATUS_MOVED: int = 3


class TreedBuilder(AdaNodeVisitor):
    __root: AdaNode
    __visit_doc_tags: bool
    tree: dict[AdaNode, list[AdaNode]]
    tree_height: dict[AdaNode, int]
    tree_depth: dict[AdaNode, int]
    tree_vector: dict[AdaNode, dict[str, int]]
    tree_root_vector: dict[AdaNode, dict[str, int]]

    def __init__(self, root: AdaNode, visit_doc_tags: bool):
        self.tree = dict()
        self.tree_height = dict()
        self.tree_depth = dict()
        self.tree_vector = dict()
        self.tree_root_vector = dict()
        self.__root = root
        self.__visit_doc_tags = visit_doc_tags
        self.tree_depth[root] = 0

    @overrides
    def pre_visit(self, node: AdaNode):
        self.tree[node] = []
        if node != self.__root:
            self.tree_depth[node] = self.tree_depth[node.parent] + 1

    @overrides
    def post_visit(self, node: AdaNode):
        self.build_tree(node)
        self.build_tree_height(node)
        self.__build_vector(node)

    def build_tree(self, node: AdaNode):
        if node != self.__root:
            parent: AdaNode = node.parent
            children: list[AdaNode] = self.tree.get(parent)
            children.append(node)

    def build_tree_height(self, node: AdaNode):
        children: list[AdaNode] = self.tree.get(node)
        maximum: int = 0
        for child in children:
            height: int = self.tree_height.get(child)
            if height > maximum:
                maximum = height
        self.tree_height[node] = maximum + 1

    def __build_vector(self, node: AdaNode):
        children: list[AdaNode] = self.tree[node]
        vector: dict[str, int] = dict()
        root_vector: dict[str, int] = dict()
        label: int = TreedUtils.build_label_for_vector(node)
        feature: str = chr(label)
        root_vector[feature] = 1
        for child in children:
            self.__add(vector, self.tree_vector[child])
            child_root_vector: dict[str, int] = self.tree_root_vector[child]
            for cf in child_root_vector.keys():
                if len(cf) < TreedConstants.GRAM_MAX_LENGTH:
                    rf: str = chr(label) + cf
                    root_vector[rf] = child_root_vector[cf]
            child_root_vector.clear()
            del self.tree_root_vector[child]
        self.__add(vector, root_vector)
        self.tree_vector[node] = vector
        self.tree_root_vector[node] = root_vector

    @staticmethod
    def __add(vector: dict[str, int], other: dict[str, int]):
        for key in other.keys():
            if key in vector.keys():
                vector[key] += other[key]
            else:
                vector[key] = other[key]


class MapMovingVisitor(AdaNodeVisitor):
    treed_mapper: TreedMapper

    def __init__(self, treed_mapper: TreedMapper):
        self.treed_mapper = treed_mapper

    def visit(self, node: SubpBody) -> bool:
        maps: dict[AdaNode, float] = self.treed_mapper.get_tree_map()[node]
        if maps:
            mapped: AdaNode = next(iter(maps.keys()))
            self.treed_mapper.map_moving1(node, mapped)
            return False
        return True


class PrintVisitor(AdaNodeVisitor):
    def __init__(self, treed_mapper: TreedMapper):
        self.treed_mapper: TreedMapper = treed_mapper
        self.indent: int = 0

    def print_indent(self):
        for i in range(0, self.indent):
            print('\t', end='')

    def pre_visit(self, node: AdaNode):
        self.print_indent()
        status: int = self.treed_mapper.property_status.get(node)
        print('{}: {}'.format(TreedUtils.build_ast_label(node), self.treed_mapper.get_status(status)), end='')
        m_n: AdaNode = self.treed_mapper.property_map.get(node)
        if status > TreedConstants.STATUS_UNCHANGED and m_n is not None:
            print(' {}'.format(TreedUtils.build_ast_label(m_n)), end='')
        print('')
        self.indent += 1

    def post_visit(self, node: AdaNode):
        self.indent -= 1


class TreedMapper:
    __ast_m: AdaNode
    __ast_n: AdaNode
    __tree: dict[AdaNode, list[AdaNode]]
    __tree_height: dict[AdaNode, int]
    __tree_depth: dict[AdaNode, int]
    __tree_vector: dict[AdaNode, dict[str, int]]
    __tree_map: dict[AdaNode, dict[AdaNode, float]]
    __pivots_m: set[AdaNode]
    __pivots_n: set[AdaNode]
    __name_map_frequency: dict[str, dict[str, int]]
    __name_frequency: dict[str, int]
    __rename_map: dict[str, str]
    __pivot_copy: dict[AdaNode, dict[AdaNode, float]]
    __number_of_changes: int
    __number_of_unmaps: int
    __number_of_non_name_unmaps: int
    __visit_doc_tags: bool = False
    property_map: dict[AdaNode, AdaNode]
    property_status: dict[AdaNode, int]

    def __init__(self, ast_m: AdaNode, ast_n: AdaNode, source_m, source_n):
        self.__tree = dict()
        self.__tree_height = dict()
        self.__tree_depth = dict()
        self.__tree_vector = dict()
        self.__tree_map = dict()
        self.__pivots_m = set()
        self.__pivots_n = set()
        self.__name_map_frequency = dict()
        self.__name_frequency = dict()
        self.__rename_map = dict()
        self.__pivot_copy = dict()
        self.__number_of_changes = 0
        self.__number_of_unmaps = 0
        self.__number_of_non_name_unmaps = 0
        self.__ast_m = ast_m
        self.__ast_n = ast_n
        self.__lines_m = source_m.splitlines()
        self.__lines_n = source_n.splitlines()
        self.property_map = {}
        self.property_status = {}

    def get_tree_map(self):
        return self.__tree_map

    def get_number_of_changes(self) -> int:
        return self.__number_of_changes

    def get_number_of_unmaps(self) -> int:
        return self.__number_of_unmaps

    def get_number_of_non_name_unmaps(self) -> int:
        return self.__number_of_non_name_unmaps

    def is_changed(self) -> bool:
        return self.__number_of_changes > 0

    def has_unmaps(self) -> bool:
        return self.__number_of_unmaps > 0

    def has_non_name_unmap(self) -> bool:
        return self.__number_of_non_name_unmaps > 0

    def map(self, visit_doc_tags: bool = False):
        self.__visit_doc_tags = visit_doc_tags
        self.__build_trees(visit_doc_tags)
        self._map_pivots()
        self.__map_bottom_up()
        self._map_moving()
        self._map_top_down()
        self._mark_changes()

    @multimethod
    def print_changes(self):
        self.print_changes(self.__ast_m)
        print('')
        self.print_changes(self.__ast_n)

    @multimethod
    def print_changes(self, node: AdaNode):
        print_visitor: PrintVisitor = PrintVisitor(self)
        accept(node, print_visitor)

    @staticmethod
    def get_status(status: int) -> str:
        if status == TreedConstants.STATUS_MOVED:
            return "MOVED"
        elif status == TreedConstants.STATUS_RELABELED:
            return "RELABELED"
        elif status == TreedConstants.STATUS_UNCHANGED:
            return "UNCHANGED"
        elif status == TreedConstants.STATUS_UNMAPPED:
            return "UNMAPPED"
        else:
            return "NOTHING_ELSE"

    def _mark_changes(self):
        self.__mark_changes1(self.__ast_m)
        self.__detect_renaming()
        self.__mark_unmapped(self.__ast_n)

    def __detect_renaming(self):
        imap: dict[str, set[str]] = dict()
        for name_m in self.__name_frequency.keys():
            f: int = self.__name_frequency[name_m]
            mapped: Optional[str] = None
            map_frequency: dict[str, int] = self.__name_map_frequency[name_m]
            for name_n in map_frequency.keys():
                if self.__is_same_name(name_m, name_n):
                    mapped = name_n
                    break
                mf: int = self.__name_map_frequency[name_m][name_n]
                if mf > f * TreedConstants.MIN_SIMILARITY:
                    mapped = name_n
            if mapped is not None:
                self.__rename_map[name_m] = mapped
                s: set[str] = imap.get(mapped, None)
                if s is None:
                    s = set()
                    imap[mapped] = s
                s.add(name_m)
        for name_m in set(self.__rename_map.keys()):
            name_n: str = self.__rename_map[name_m]
            if self.__is_same_name(name_m, name_n):
                del self.__rename_map[name_m]
                continue
            for iname in imap[name_n]:
                if self.__is_same_name(iname, name_n):
                    del self.__rename_map[name_m]
                    break

    @staticmethod
    def __is_same_name(name_m: str, name_n: str) -> bool:
        # TODO this doesn't make sense for Ada.
        index_m: int = name_m.rfind('#')
        index_n: int = name_n.rfind('#')
        if index_m == -1 and index_n == -1:
            return name_m == name_n
        if index_m > -1 and index_n > -1:
            return name_m[index_m:] == name_n[index_n:]
        return False

    def __mark_unmapped(self, node: AdaNode):
        if self.property_status.get(node) is None:
            self.property_status[node] = TreedConstants.STATUS_UNMAPPED
            self.__number_of_changes += 1
            self.__number_of_unmaps += 1
            # TODO: SimpleName in original
            if not node.is_a(Identifier):
                self.__number_of_non_name_unmaps += 1
        # TODO: SimpleName in original
        elif node.is_a(Identifier):
            mapped_node: Identifier = self.property_map.get(node)
            if mapped_node is not None and not self.__check_name_map(mapped_node, node):
                self.property_map[node] = None
                self.property_status[node] = TreedConstants.STATUS_UNMAPPED
                self.property_map[mapped_node] = None
                self.property_status[mapped_node] = TreedConstants.STATUS_UNMAPPED
        children: list[AdaNode] = self.__tree.get(node)
        for child in children:
            self.__mark_unmapped(child)

    @multimethod
    def __mark_changes1(self, node: AdaNode):
        maps: dict[AdaNode, float] = self.__tree_map.get(node)
        if not maps:
            self.property_status[node] = TreedConstants.STATUS_UNMAPPED
            self.__number_of_changes += 1
            self.__number_of_unmaps += 1
            # TODO: identifier is SimpleName in original
            if not node.is_a(Identifier) and not node.is_a(ReturnStmt) and not node.is_a(ExitStmt):
                self.__number_of_non_name_unmaps += 1
        else:
            mapped_node: AdaNode = next(iter(maps.keys()))
            self.property_map[node] = mapped_node
            self.property_map[mapped_node] = node
            self.__update_name_map(node, mapped_node)
            if node == self.__ast_m:
                self.property_status[self.__ast_m] = TreedConstants.STATUS_UNCHANGED
                self.property_status[self.__ast_n] = TreedConstants.STATUS_UNCHANGED
            else:
                p: AdaNode = node.parent
                mp: AdaNode = mapped_node.parent
                if mp not in self.__tree_map.get(p):
                    self.property_status[node] = TreedConstants.STATUS_MOVED
                    self.property_status[mapped_node] = TreedConstants.STATUS_MOVED
                    self.__number_of_changes += 2
                else:
                    if self.property_status.get(node) is None:
                        self.property_status[node] = TreedConstants.STATUS_MOVED
                        self.property_status[mapped_node] = TreedConstants.STATUS_MOVED
                        self.__number_of_changes += 2
            # mark moving for children
            children: list[AdaNode] = self.__tree.get(node)
            mapped_children: list[AdaNode] = self.__tree.get(mapped_node)
            if children and mapped_children:
                self.__mark_changes2(children, mapped_children)
        children: list[AdaNode] = self.__tree.get(node)
        for child in children:
            self.__mark_changes1(child)

    @multimethod
    def __mark_changes2(self, nodes: list[AdaNode], mapped_nodes: list[AdaNode]):
        d: list[list[int]] = [[0 for _ in range(len(mapped_nodes) + 1)] for _ in range(2)]
        p: list[list[Optional[str]]] = [[None for _ in range(len(mapped_nodes) + 1)] for _ in range(len(nodes) + 1)]
        for i in range(1, len(nodes) + 1):
            node: AdaNode = nodes[i - 1]
            maps: dict[AdaNode, float] = self.__tree_map[node]
            for j in range(0, len(mapped_nodes) + 1):
                d[0][j] = d[1][j]
            for j in range(1, len(mapped_nodes) + 1):
                node_n: AdaNode = mapped_nodes[j - 1]
                if node_n in maps:
                    d[1][j] = d[0][j - 1] + 1
                    p[i][j] = 'D'
                elif d[0][j] > d[1][j - 1]:
                    d[1][j] = d[0][j]
                    p[i][j] = 'U'
                else:
                    d[1][j] = d[1][j - 1]
                    p[i][j] = 'L'
        i: int = len(nodes)
        j: int = len(mapped_nodes)
        while i > 0 and j > 0:
            if p[i][j] == 'D':
                node: AdaNode = nodes[i - 1]
                node2: AdaNode = mapped_nodes[j - 1]
                if TreedUtils.build_label_for_vector(node) == TreedUtils.build_label_for_vector(node2):
                    self.property_status[node] = TreedConstants.STATUS_UNCHANGED
                    self.property_status[node2] = TreedConstants.STATUS_UNCHANGED
                else:
                    self.property_status[node] = TreedConstants.STATUS_RELABELED
                    self.property_status[node2] = TreedConstants.STATUS_RELABELED
                    self.__number_of_changes += 2
                i -= 1
                j -= 1
            elif p[i][j] == 'U':
                i -= 1
            else:
                j -= 1

    def __update_name_map(self, node_m: AdaNode, node_n: AdaNode):
        if isinstance(node_m, Identifier):
            name_m: str = node_m.text
            name_n: str = node_n.text
            map_frequency: dict[str, int] = self.__name_map_frequency.get(name_m, None)
            i_map_frequency: dict[str, int] = self.__name_map_frequency.get(name_n, None)
            if map_frequency is None:
                map_frequency = dict()
                self.__name_map_frequency[name_m] = map_frequency
            if i_map_frequency is None:
                i_map_frequency = dict()
                self.__name_map_frequency[name_n] = i_map_frequency
            c: int = map_frequency.get(name_n, 0)
            c += 1
            map_frequency[name_n] = c
            i_map_frequency[name_n] = c
            c = self.__name_frequency.get(name_m, 0)
            self.__name_frequency[name_m] = c + 1

    def __check_name_map(self, node_m: AdaNode, node_n: AdaNode):
        if node_m.text == node_n.text:
            return True
        return node_n.text == self.__rename_map.get(node_m.text, None)

    # not sure why this can not be a multimethod?
    def _map_pivots(self):
        for node in self.__tree.keys():
            self.__tree_map[node] = dict()
        self.__set_map(self.__ast_m, self.__ast_n, 1.0)
        nodes_m: list[AdaNode] = self.__get_children_containers(self.__ast_m)
        nodes_n: list[AdaNode] = self.__get_children_containers(self.__ast_n)
        heights_m: list[AdaNode] = nodes_m.copy()
        heights_n: list[AdaNode] = nodes_n.copy()
        heights_m.sort(key=lambda x: self.__tree_height[x], reverse=True)
        heights_n.sort(key=lambda x: self.__tree_height[x], reverse=True)
        self.__map_pivots(nodes_m, nodes_n, heights_m, heights_n)

    def __map_pivots(self, nodes_m: list[AdaNode], nodes_n: list[AdaNode], heights_m: list[AdaNode],
                     heights_n: list[AdaNode]):
        lcs_m: list[int] = []
        lcs_n: list[int] = []
        self.__lcs(nodes_m, nodes_n, lcs_m, lcs_n)
        for i in reversed(range(0, len(lcs_m))):
            index_m: int = lcs_m[i]
            index_n: int = lcs_n[i]
            node_m: AdaNode = nodes_m[index_m]
            node_n: AdaNode = nodes_n[index_n]
            self.__set_map(node_m, node_n, 1.0)
            self.__pivots_m.add(node_m)
            self.__pivots_n.add(node_n)
            del nodes_m[index_m]
            del nodes_n[index_n]
            heights_m.remove(node_m)
            heights_n.remove(node_n)
        while nodes_m and nodes_n:
            height_m: int = self.__tree_height.get(heights_m[0])
            height_n: int = self.__tree_height.get(heights_n[0])
            expanded_m: bool = False
            expanded_n: bool = False
            if height_m >= height_n:
                expanded_m = self.__expand_for_pivots(nodes_m, heights_m, height_m)
            if height_n >= height_m:
                expanded_n = self.__expand_for_pivots(nodes_n, heights_n, height_n)
            if expanded_m or expanded_n:
                self.__map_pivots(nodes_m, nodes_n, heights_m, heights_n)
                break

    def __expand_for_pivots(self, node_list: list[AdaNode], heights: list[AdaNode], h: int) -> bool:
        nodes: set[AdaNode] = set()
        for node in heights:
            if self.__tree_height.get(node) == h:
                nodes.add(node)
            else:
                break
        expanded: bool = False
        for i in reversed(range(0, len(node_list))):
            node: AdaNode = node_list[i]
            if node in nodes:
                del node_list[i]
                del heights[0]
                children: list[AdaNode] = self.__get_children_containers(node)
                if children:
                    expanded = True
                    for j in range(0, len(children)):
                        child: AdaNode = children[j]
                        node_list.append(child)
                        insort(heights, child, key=lambda n: self.__tree_height.get(n) * -1)
        return expanded

    def __expand_for_moving(self, node_list: list[AdaNode], heights: list[AdaNode], h: int) -> bool:
        nodes: set[AdaNode] = set()
        for node in heights:
            if self.__tree_height.get(node) == h:
                nodes.add(node)
            else:
                break
        expanded: bool = False
        for i in reversed(range(0, len(node_list))):
            node: AdaNode = node_list[i]
            if node in nodes:
                del node_list[i]
                del heights[0]
                children: list[AdaNode] = self.__get_not_yet_mapped_descendant_containers(node)
                if children:
                    expanded = True
                    for j in range(0, len(children)):
                        child: AdaNode = children[j]
                        node_list.append(child)
                        insort(heights, child, key=lambda n: self.__tree_height.get(n) * -1)
        return expanded

    def __lcs(self, nodes_m: list[AdaNode], nodes_n: list[AdaNode], lcs_m: list[int], lcs_n: list[int]):
        d: list[list[int]] = [[0 for _ in range(len(nodes_n) + 1)] for _ in range(2)]
        p: list[list[Optional[str]]] = [[None for _ in range(len(nodes_n) + 1)] for _ in range(len(nodes_m) + 1)]
        for i in reversed(range(0, len(nodes_m))):
            node_m: AdaNode = nodes_m[i]
            height_m: int = self.__tree_height.get(node_m)
            vector_m: dict[str, int] = self.__tree_vector.get(node_m)
            for j in range(0, len(nodes_n) + 1):
                d[0][j] = d[1][j]
            for j in reversed(range(0, len(nodes_n))):
                node_n: AdaNode = nodes_n[j]
                height_n: int = self.__tree_height.get(node_n)
                vector_n: dict[str, int] = self.__tree_vector.get(node_n)
                if height_m == height_n and node_m.kind_name == node_n.kind_name and vector_m == vector_n and match(node_m, node_n):
                    d[1][j] = d[0][j + 1] + 1
                    p[i][j] = 'D'
                elif d[0][j] >= d[1][j + 1]:
                    d[1][j] = d[0][j]
                    p[i][j] = 'U'
                else:
                    d[1][j] = d[1][j + 1]
                    p[i][j] = 'R'
        i: int = 0
        j: int = 0
        while i < len(nodes_m) and j < len(nodes_n):
            if p[i][j] == 'D':
                lcs_m.append(i)
                lcs_n.append(j)
                i += 1
                j += 1
            elif p[i][j] == 'U':
                i += 1
            else:
                j += 1

    def __get_children_containers(self, node: AdaNode) -> list[AdaNode]:
        children: list[AdaNode] = []
        for child in self.__tree.get(node):
            if self.__tree_height.get(child) >= TreedConstants.MIN_HEIGHT:
                children.append(child)
        return children

    def __compare_nodes(self, node1: AdaNode, node2: AdaNode) -> int:
        d: int = self.__tree_height.get(node2) - self.__tree_height.get(node1)
        if d != 0:
            return d
        d = self.__tree_depth.get(node1) - self.__tree_depth.get(node2)
        if d != 0:
            return d
        if node1.sloc_range.start.line == node2.sloc_range.start.line:
            return node1.sloc_range.start.column - node2.sloc_range.start.column
        else:
            return node1.sloc_range.start.line - node2.sloc_range.start.line

    def __map_bottom_up(self):
        heights_m: list[AdaNode] = list(self.__pivots_m)
        heights_m.sort(key=cmp_to_key(self.__compare_nodes))
        for node_m in heights_m:
            node_n: AdaNode = next(iter(self.__tree_map.get(node_m).keys()))
            ancestors_m: list[AdaNode] = []
            ancestors_n: list[AdaNode] = []
            self.__get_not_yet_mapped_ancestors(node_m, ancestors_m)
            self.__get_not_yet_mapped_ancestors(node_n, ancestors_n)
            self.__map(ancestors_m, ancestors_n, TreedConstants.MIN_SIMILARITY)

    @staticmethod
    def __start_position(node: AdaNode, lines) -> int:
        start_position: int = 0
        if node.sloc_range.start.line - 1 > len(lines):
            print("that's weird!")
        for i in range(0, node.sloc_range.start.line - 1):
            start_position += len(lines[i])
        start_position += node.sloc_range.start.column
        return start_position

    def __map(self, nodes_m: list[AdaNode], nodes_n: list[AdaNode], threshold: float) -> list[AdaNode]:
        pairs_of_ancestor: dict[AdaNode, set[Pair]] = dict()
        pairs: list[Pair] = []
        for node_m in nodes_m:
            pairs1: set[Pair] = set()
            for node_n in nodes_n:
                similarity: float = self._compute_similarity(node_m, node_n, threshold)
                if similarity >= threshold:
                    pair: Pair = Pair(node_m, node_n, similarity,
                                      - abs((self.__start_position(node_m.parent, self.__lines_m) - self.__start_position(node_m, self.__lines_m)) -
                                            (self.__start_position(node_n.parent, self.__lines_n) - self.__start_position(node_n, self.__lines_n))))
                    pairs1.add(pair)
                    pairs2: set[Pair] = pairs_of_ancestor.get(node_n, set())
                    pairs2.add(pair)
                    pairs_of_ancestor[node_n] = pairs2
                    pairs.append(pair)
            pairs_of_ancestor[node_m] = pairs1
        pairs.sort(reverse=True)
        nodes: list[AdaNode] = []
        while pairs:
            pair: Pair = pairs[0]
            node_m: AdaNode = cast(AdaNode, pair.get_object1())
            node_n: AdaNode = cast(AdaNode, pair.get_object2())
            self.__set_map(node_m, node_n, pair.get_weight())
            nodes.append(node_m)
            nodes.append(node_n)
            for p in pairs_of_ancestor.get(node_m):
                if p in pairs:
                    pairs.remove(p)
            for p in pairs_of_ancestor.get(node_n):
                if p in pairs:
                    pairs.remove(p)
        return nodes

    def __set_map(self, node_m: AdaNode, node_n: AdaNode, w: float):
        self.__tree_map[node_m][node_n] = w
        self.__tree_map[node_n][node_m] = w

    def _compute_similarity(self, node_m: AdaNode, node_n: AdaNode, threshold: float) -> float:
        if node_m.kind_name != node_n.kind_name:
            return 0.0
        children_m: list[AdaNode] = self.__tree[node_m]
        children_n: list[AdaNode] = self.__tree[node_n]
        if not children_m and not children_n:
            # TODO: Modifier?
            similarity: float = 0.0
            if node_m.is_a(BinOp):
                similarity = TreedConstants.MIN_SIMILARITY_MOVE
            else:
                text_m: str = node_m.text
                text_n: str = node_n.text
                if len(text_m) > 1000 or len(text_n) > 1000:
                    if len(text_m) == 0 and len(text_n) == 0:
                        similarity = 1.0
                    elif len(text_m) == 0 or len(text_n) == 0:
                        similarity = 0.0
                    else:
                        similarity = len(text_n) * 1.0 / len(text_m) if len(text_m) > len(text_n) else len(text_m) * 1.0 / len(text_n)
                elif len(text_m) == 0 and len(text_n) == 0:
                    similarity = 1.0
                else:
                    similarity = compute_char_lcs(serialize_to_chars(text_m), serialize_to_chars(text_n))
            similarity = threshold + similarity * (1 - threshold)
            return similarity
        if children_m and children_n:
            vector_m: dict[str, int] = self.__tree_vector.get(node_m)
            vector_n: dict[str, int] = self.__tree_vector.get(node_n)
            similarity: float = self.__compute_similarity(vector_m, vector_n)
            similarities: list[float] = self.__compute_vector_similarity(children_m, children_n)
            for s in similarities:
                similarity += s
            return similarity / (len(similarities) + 1)
        return 0.0

    def __compute_vector_similarity(self, l1: list[AdaNode], l2: list[AdaNode]) -> list[float]:
        similarities: list[float] = [0.0 for _ in range(max(len(l1), len(l2)))]
        pairs_of_node: dict[AdaNode, set[Pair]] = dict()
        pairs: list[Pair] = []
        for node1 in l1:
            pairs1: set[Pair] = set()
            for node2 in l2:
                similarity: float = self.__compute_similarity(self.__tree_vector[node1], self.__tree_vector[node2])
                if similarity > 0:
                    pair: Pair = Pair(node1, node2, similarity)
                    pairs1.add(pair)
                    pairs2: set[Pair] = pairs_of_node.get(node2, set())
                    pairs2.add(pair)
                    pairs_of_node[node2] = pairs2
                    pairs.append(pair)
            pairs_of_node[node1] = pairs1
        pairs.sort(reverse=True)
        i: int = 0
        pairs_copy = pairs.copy()
        while pairs:
            pair: Pair = pairs[0]
            try:
                similarities[i] = pair.get_weight()
            except:
                print('huh?')
            i += 1
            for p in pairs_of_node[cast(AdaNode, pair.get_object1())]:
                if p in pairs:
                    pairs.remove(p)
            for p in pairs_of_node[cast(AdaNode, pair.get_object2())]:
                if p in pairs:
                    pairs.remove(p)
        return similarities

    @staticmethod
    def __compute_similarity(vector_m: dict[str, int], vector_n: dict[str, int]) -> float:
        similarity: float = 0.0
        keys: set[str] = set(vector_m.keys()).intersection(set(vector_n.keys()))
        for key in keys:
            similarity += min(vector_m[key], vector_n[key])
        similarity = (2 * (similarity + TreedConstants.SIMILARITY_SMOOTH)) / (
                    len(vector_m) + len(vector_n) + 2 * TreedConstants.SIMILARITY_SMOOTH)
        return similarity

    @staticmethod
    def __length(vector: dict[object, int]) -> int:
        length: int = 0
        for value in vector.values():
            length += value
        return length

    def __get_not_yet_mapped_ancestors(self, node: AdaNode, ancestors: list[AdaNode]):
        parent: AdaNode = node.parent
        if len(self.__tree_map[parent]) == 0:
            ancestors.append(parent)
            self.__get_not_yet_mapped_ancestors(parent, ancestors)

    @multimethod
    def _map_top_down(self):
        self.__map_top_down(self.__ast_m)

    @multimethod
    def __map_top_down(self, node_m: AdaNode):
        children_m: list[AdaNode] = self.__tree.get(node_m)
        maps: dict[AdaNode, float] = self.__tree_map.get(node_m)
        if maps:
            node_n: AdaNode = next(iter(maps.keys()))
            children_n: list[AdaNode] = self.__tree.get(node_n)
            if node_m in self.__pivots_n:
                self.__map_unchanged_nodes(node_m, node_n)
                return
            else:
                nodes_m: list[AdaNode] = self.__get_not_yet_matched_nodes(children_m)
                nodes_n: list[AdaNode] = self.__get_not_yet_matched_nodes(children_n)
                mapped_children_m: list[AdaNode] = []
                mapped_children_n: list[AdaNode] = []
                if node_m.is_a(Stmt):
                    # if node_m.is_a(ForLoopStmt):
                    #     mapped_children_m.append(cast(WhileLoopStmt, node_m).)
                    #     mapped_children_n.append()
                    pass
                elif node_m.is_a(SubpBody):
                    # mapped_children_m.append(cast(SubpBody, node_m).f_subp_spec)
                    # mapped_children_m.append(cast(SubpBody, node_m).f_decls)
                    # mapped_children_m.append(cast(SubpBody, node_m).f_stmts)
                    # mapped_children_n.append(cast(SubpBody, node_n).f_subp_spec)
                    # mapped_children_n.append(cast(SubpBody, node_n).f_decls)
                    # mapped_children_n.append(cast(SubpBody, node_n).f_stmts)
                    pass
                elif node_m.is_a(ObjectDecl):
                    # mapped_children_m.append(cast(ObjectDecl, node_m).f_ids)
                    # mapped_children_n.append(cast(ObjectDecl, node_n).f_ids)
                    pass
                elif node_m.is_a(DefiningName):
                    # mapped_children_m.append(cast(DefiningName, node_m).f_name)
                    # mapped_children_n.append(cast(DefiningName, node_n).f_name)
                    pass
                elif node_m.is_a(Expr):
                    pass
                if mapped_children_m and mapped_children_n:
                    for i in range(0, len(mapped_children_m)):
                        child_m: AdaNode = mapped_children_m[i]
                        child_n: AdaNode = mapped_children_n[i]
                        if child_m is not None and child_n is not None:
                            if len(self.__tree_map.get(child_m)) == 0 and len(self.__tree_map.get(child_n)) == 0:
                                similarity: float = 0.0
                                if child_m.kind_name == child_n.kind_name:
                                    if node_m.is_a(BlockStmt) or (len(self.__tree_map.get(child_m)) == 0 and len(self.__tree_map.get(child_n)) == 0):
                                        similarity = 1.0
                                    else:
                                        similarity = self._compute_similarity(child_m, child_n, TreedConstants.MIN_SIMILARITY)
                                    if similarity >= TreedConstants.MIN_SIMILARITY:
                                        self.__set_map(child_m, child_n, TreedConstants.MIN_SIMILARITY)
                                        if TreedUtils.build_ast_label(child_m) == TreedUtils.build_ast_label(child_n):
                                            # TODO: Should this not be PROPERTY_STATUS?
                                            self.property_map[child_m] = TreedConstants.STATUS_UNCHANGED
                                            self.property_map[child_n] = TreedConstants.STATUS_UNCHANGED
                                        else:
                                            # TODO: Should this not be PROPERTY_STATUS?
                                            self.property_map[child_m] = TreedConstants.STATUS_RELABELED
                                            self.property_map[child_n] = TreedConstants.STATUS_RELABELED
                                if similarity < TreedConstants.MIN_SIMILARITY:
                                    temp_m: list[AdaNode] = []
                                    temp_n: list[AdaNode] = []
                                    temp_m.append(child_m)
                                    temp_n.append(child_n)
                                    height_m: int = self.__tree_height.get(child_m)
                                    height_n: int = self.__tree_height.get(child_n)
                                    if height_m >= height_n:
                                        temp_m.remove(child_m)
                                        temp_m.extend(self.__get_not_yet_matched_nodes(self.__tree.get(child_m)))
                                    if height_n >= height_m:
                                        temp_n.remove(child_n)
                                        temp_n.extend(self.__get_not_yet_matched_nodes(self.__tree.get(child_n)))
                                    mapped_nodes: list[AdaNode] = self.__map(temp_m, temp_n, TreedConstants.MIN_SIMILARITY_MOVE)
                                    for j in range(0, len(mapped_nodes), 2):
                                        mapped_node_m: AdaNode = mapped_nodes[j]
                                        mapped_node_n: AdaNode = mapped_nodes[j+1]
                                        temp_m.remove(mapped_node_m)
                                        temp_n.remove(mapped_node_n)
                        if child_m in nodes_m:
                            nodes_m.remove(child_m)
                        if child_n in nodes_n:
                            nodes_n.remove(child_n)
                lcs_m: list[int] = []
                lcs_n: list[int] = []
                self.__lcs(nodes_m, nodes_n, lcs_m, lcs_n)
                for i in reversed(range(0, len(lcs_m))):
                    i_m: int = lcs_m[i]
                    i_n: int = lcs_n[i]
                    n_m: AdaNode = nodes_m[i_m]
                    n_n: AdaNode = nodes_n[i_n]
                    self.__set_map(n_m, n_n, 1.0)
                    del nodes_m[i_m]
                    del nodes_n[i_n]
                # DELETED CODE? 875 - 883
                lcs_m.clear()
                lcs_n.clear()
                mapped_nodes: list[AdaNode] = self.__map(nodes_m, nodes_n, TreedConstants.MIN_SIMILARITY)
                for i in range(0, len(mapped_nodes), 2):
                    mapped_node_m: AdaNode = mapped_nodes[i]
                    mapped_node_n: AdaNode = mapped_nodes[i+1]
                    if mapped_node_m in nodes_m:
                        nodes_m.remove(mapped_node_m)
                    if mapped_node_n in nodes_n:
                        nodes_n.remove(mapped_node_n)
                maxs_m: list[AdaNode] = []
                maxs_n: list[AdaNode] = []
                max_height_m: int = self.__max_height(nodes_m, maxs_m)
                max_height_n: int = self.__max_height(nodes_n, maxs_n)
                if max_height_m >= max_height_n:
                    for node in maxs_m:
                        nodes_m.remove(node)
                        nodes_m.extend(self.__get_not_yet_matched_nodes(self.__tree.get(node)))
                if max_height_n >= max_height_m:
                    for node in maxs_n:
                        nodes_n.remove(node)
                        nodes_n.extend(self.__get_not_yet_matched_nodes(self.__tree.get(node)))
                mapped_nodes = self.__map(nodes_m, nodes_n, TreedConstants.MIN_SIMILARITY_MOVE)
                for i in range(0, len(mapped_nodes), 2):
                    mapped_node_m: AdaNode = mapped_nodes[i]
                    mapped_node_n: AdaNode = mapped_nodes[i+1]
                    if mapped_node_m in nodes_m:
                        nodes_m.remove(mapped_node_m)
                    if mapped_node_n in nodes_n:
                        nodes_n.remove(mapped_node_n)
        for child in children_m:
            self.__map_top_down(child)

    def __max_height(self, nodes: list[AdaNode], maxima: list[AdaNode]) -> int:
        maximum: int = 0
        for node in nodes:
            h: int = self.__tree_height[node]
            if h >= maximum:
                if h > maximum:
                    maximum = h
                    maxima.clear()
                maxima.append(node)
        return maximum

    def __map_unchanged_nodes(self, node_m: AdaNode, node_n: AdaNode):
        self.__set_map(node_m, node_n, 1.0)
        children_m: list[AdaNode] = self.__tree[node_m]
        children_n: list[AdaNode] = self.__tree[node_n]
        for i in range(0, len(children_m)):
            self.__map_unchanged_nodes(children_m[i], children_n[i])

    def __get_not_yet_matched_nodes(self, nodes: list[AdaNode]):
        not_yet_mapped_nodes: list[AdaNode] = []
        for node in nodes:
            if len(self.__tree_map[node]) == 0:
                not_yet_mapped_nodes.append(node)
        return not_yet_mapped_nodes

    # again, multimethod not working?
    def _map_moving(self):
        visitor: MapMovingVisitor = MapMovingVisitor(self)
        accept(self.__ast_m, visitor)

    def map_moving1(self, ast_m: AdaNode, ast_n: AdaNode):
        list_m: list[AdaNode] = self.__get_not_yet_mapped_descendant_containers(ast_m)
        list_n: list[AdaNode] = self.__get_not_yet_mapped_descendant_containers(ast_n)
        heights_m: list[AdaNode] = list_m.copy()
        heights_n: list[AdaNode] = list_n.copy()
        heights_m.sort(key=lambda x: self.__tree_height[x], reverse=True)
        heights_n.sort(key=lambda x: self.__tree_height[x], reverse=True)
        self.map_moving2(list_m, list_n, heights_m, heights_n)

    def map_moving2(self, list_m: list[AdaNode], list_n: list[AdaNode], heights_m: list[AdaNode],
                     heights_n: list[AdaNode]):
        mapped_nodes: list[AdaNode] = self.__map(list_m, list_n, TreedConstants.MIN_SIMILARITY_MOVE)
        for i in range(0, len(mapped_nodes), 2):
            node_m: AdaNode = mapped_nodes[i]
            node_n: AdaNode = mapped_nodes[i + 1]
            if node_m in list_m:
                list_m.remove(node_m)
            if node_n in list_n:
                list_n.remove(node_n)
            if node_m in heights_m:
                heights_m.remove(node_m)
            if node_n in heights_n:
                heights_n.remove(node_n)
        while len(list_m) > 0 and len(list_n) > 0:
            height_m: int = self.__tree_height[heights_m[0]]
            height_n: int = self.__tree_height[heights_n[0]]
            expanded_m: bool = False
            expanded_n: bool = False
            if height_m >= height_n:
                expanded_m = self.__expand_for_moving(list_m, heights_m, height_m)
            if height_n >= height_m:
                expanded_n = self.__expand_for_moving(list_n, heights_n, height_n)
            if expanded_m or expanded_n:
                self.map_moving2(list_m, list_n, heights_m, heights_n)
                break

    def __get_not_yet_mapped_descendant_containers(self, node: AdaNode) -> list[AdaNode]:
        children: list[AdaNode] = []
        for child in self.__tree[node]:
            if child not in self.__pivots_m and child not in self.__pivots_n and \
                    self.__tree_height[child] >= TreedConstants.MIN_HEIGHT:
                if len(self.__tree_map[child]) == 0:
                    children.append(child)
                else:
                    children.extend(self.__get_not_yet_mapped_descendant_containers(child))
        return children

    def __build_trees(self, visit_doc_tags: bool):
        self.__build_tree(self.__ast_m, visit_doc_tags)
        self.__build_tree(self.__ast_n, visit_doc_tags)

    def __build_tree(self, root: AdaNode, visit_doc_tags: bool):
        visitor: TreedBuilder = TreedBuilder(root, visit_doc_tags)
        accept(root, visitor)
        self.__tree.update(visitor.tree)
        self.__tree_height.update(visitor.tree_height)
        self.__tree_depth.update(visitor.tree_depth)
        self.__tree_vector.update(visitor.tree_vector)


class TreedUtils:
    build_ast_label_warned = False
    build_label_for_vector_warned = False

    @staticmethod
    def build_label_for_vector(node: AdaNode) -> int:
        label: int = list(_kind_to_astnode_cls.keys())[list(_kind_to_astnode_cls.values()).index(node.__class__)]
        if node.is_a(Expr):
            if node.kind_name.endswith('Literal'):
                return (label | (hash(node.text) << 7)) & 0x10ffff
            if node.is_a(Identifier):
                return (label | (hash(node.text) << 7)) & 0x10ffff
        if not TreedUtils.build_label_for_vector_warned:
            logger.warning('build_label_for_vector not fully implemented.')
            TreedUtils.build_label_for_vector_warned = True
        return label

    @staticmethod
    def build_ast_label(node: AdaNode) -> str:
        label: str = node.kind_name
        if node.is_a(Expr):
            if label.endswith('Literal'):
                return '{}({})'.format(label, node.text)
            if node.is_a(BinOp):
                return '{}({})'.format(label, cast(BinOp, node).f_op.text)
            if node.is_a(Identifier):
                return '{}({})'.format(label, node.text)
            if not TreedUtils.build_ast_label_warned:
                logger.warning('build_ast_label not fully implemented.')
                TreedUtils.build_ast_label_warned = True
        return label
