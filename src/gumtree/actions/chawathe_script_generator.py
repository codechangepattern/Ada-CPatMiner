from collections import namedtuple
from typing import List, Set, Dict, Optional, Tuple

from gumtree.actions.edit_script import EditScript
from gumtree.actions.model.delete import Delete
from gumtree.actions.model.insert import Insert
from gumtree.actions.model.move import Move
from gumtree.actions.model.update import Update
from gumtree.matchers.mapping_store import MappingStore, Mapping
from gumtree.tree.fake_tree import FakeTree
from gumtree.tree.tree import Tree
from gumtree.tree.tree_utils import TreeUtils


class ChawatheScriptGenerator:

    def __init__(self):
        self.orig_src = None
        self.cpy_src = None
        self.orig_dst = None
        self.orig_mappings = None
        self.cpy_mappings = None
        self.dst_in_order = set()
        self.src_in_order = set()
        self.actions = None
        self.orig_to_copy = {}
        self.copy_to_orig = {}

    def compute_actions(self, ms) -> 'EditScript':
        self.init_with(ms)
        self.generate()
        return self.actions

    def init_with(self, ms):
        self.orig_src = ms.src
        self.cpy_src = self.orig_src.deep_copy()
        self.orig_dst = ms.dst
        self.orig_mappings = ms

        self.orig_to_copy = {}
        self.copy_to_orig = {}
        # Assuming a pre_order function exists for Tree
        cpy_tree_iterator = iter(TreeUtils.pre_order(self.cpy_src))
        for orig_tree in TreeUtils.pre_order(self.orig_src):
            cpy_tree = next(cpy_tree_iterator)
            self.orig_to_copy[orig_tree] = cpy_tree
            self.copy_to_orig[cpy_tree] = orig_tree

        self.cpy_mappings = MappingStore(ms.src, ms.dst)
        for m in self.orig_mappings:
            self.cpy_mappings.add_mapping(self.orig_to_copy[m.first], m.second)

    def generate(self):
        src_fake_root = FakeTree(self.cpy_src)
        dst_fake_root = FakeTree(self.orig_dst)
        self.cpy_src.parent = src_fake_root
        self.orig_dst.parent = dst_fake_root

        self.actions = EditScript()
        self.dst_in_order = set()
        self.src_in_order = set()

        self.cpy_mappings.add_mapping(src_fake_root, dst_fake_root)

        # Assuming a breadth_first function exists for Tree
        bfs_dst = self.orig_dst.breadth_first()
        for x in bfs_dst:
            w = None
            y = x.parent
            z = self.cpy_mappings.get_src_for_dst(y)

            if not self.cpy_mappings.is_dst_mapped(x):
                k = self.find_pos(x)
                w = FakeTree(None)  # Placeholder, adjust as needed
                ins = Insert(x, self.copy_to_orig[z], k)
                self.actions.add(ins)
                self.copy_to_orig[w] = x
                self.cpy_mappings.add_mapping(w, x)
                z.insert_child(w, k)
            else:
                w = self.cpy_mappings.get_src_for_dst(x)
                if x != self.orig_dst:
                    v = w.parent
                    if w.label != x.label:
                        self.actions.add(Update(self.copy_to_orig[w], x.label))
                        w.label = x.label
                    if z != v:
                        k = self.find_pos(x)
                        mv = Move(self.copy_to_orig[w], self.copy_to_orig[z], k)
                        self.actions.add(mv)
                        v.children.remove(w)
                        z.insert_child(w, k)
                self.src_in_order.add(w)
                self.dst_in_order.add(x)
                self.align_children(w, x)

        for w in TreeUtils.post_order(self.cpy_src):
            if not self.cpy_mappings.is_src_mapped(w):
                self.actions.add(Delete(self.copy_to_orig[w]))

        return self.actions

    def align_children(self, w, x):
        self.src_in_order -= set(w.children)
        self.dst_in_order -= set(x.children)

        s1 = [c for c in w.children if
              self.cpy_mappings.is_src_mapped(c) and self.cpy_mappings.get_dst_for_src(c) in x.children]
        s2 = [c for c in x.children if
              self.cpy_mappings.is_dst_mapped(c) and self.cpy_mappings.get_src_for_dst(c) in w.children]

        lcs_result = self.lcs(s1, s2)

        for m in lcs_result:
            self.src_in_order.add(m.first)
            self.dst_in_order.add(m.second)

        for b in s2:
            for a in s1:
                if self.cpy_mappings.has(a, b) and not Mapping(a, b) in lcs_result:
                    a.parent.children.remove(a)
                    k = self.find_pos(b)
                    mv = Move(self.copy_to_orig[a], self.copy_to_orig[w], k)
                    self.actions.add(mv)
                    w.children.insert(k, a)
                    a.parent = w
                    self.src_in_order.add(a)
                    self.dst_in_order.add(b)

    def find_pos(self, x):
        y = x.parent
        siblings = y.children

        for c in siblings:
            if c in self.dst_in_order:
                if c == x:
                    return 0
                else:
                    break

        xpos = siblings.index(x)
        v = None
        for i in range(xpos):
            c = siblings[i]
            if c in self.dst_in_order:
                v = c

        if v is None:
            return 0

        u = self.cpy_mappings.get_src_for_dst(v)
        upos = u.parent.children.index(u)

        return upos + 1

    def lcs(self, x: List[Tree], y: List[Tree]) -> List[Mapping]:
        m = len(x)
        n = len(y)
        lcs_result = []

        opt = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(m - 1, -1, -1):
            for j in range(n - 1, -1, -1):
                if self.cpy_mappings.get_src_for_dst(y[j]) == x[i]:
                    opt[i][j] = opt[i + 1][j + 1] + 1
                else:
                    opt[i][j] = max(opt[i + 1][j], opt[i][j + 1])

        i, j = 0, 0
        while i < m and j < n:
            if self.cpy_mappings.get_src_for_dst(y[j]) == x[i]:
                lcs_result.append(Mapping(x[i], y[j]))
                i += 1
                j += 1
            elif opt[i + 1][j] >= opt[i][j + 1]:
                i += 1
            else:
                j += 1

        return lcs_result

# Note: Placeholder classes EditScript, Insert, Move, Update, Delete are not provided in the given code.
