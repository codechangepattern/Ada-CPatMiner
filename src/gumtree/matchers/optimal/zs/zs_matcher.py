import math
from collections import deque
from difflib import SequenceMatcher  # Assuming this as an equivalent of StringMetrics.qGramsDistance().compare()

from gumtree.matchers.matcher import Matcher


# Need to define or import Tree and MappingStore classes somewhere here

class ZsMatcher(Matcher):
    def __init__(self):
        self.mappings = None
        self.zsSrc = None
        self.zsDst = None
        self.treeDist = None
        self.forestDist = None

    def match(self, src, dst, mappings):
        self.zsSrc = ZsTree(src)
        self.zsDst = ZsTree(dst)
        self.mappings = mappings
        self._match()
        return self.mappings

    @staticmethod
    def get_first_leaf(t):
        current = t
        while not current.is_leaf:
            current = current.get_child(0)
        return current

    def compute_tree_dist(self):
        self.treeDist = [[0 for _ in range(self.zsDst.node_count + 1)] for _ in range(self.zsSrc.node_count + 1)]
        self.forestDist = [[0 for _ in range(self.zsDst.node_count + 1)] for _ in range(self.zsSrc.node_count + 1)]

        for i in range(1, len(self.zsSrc.kr)):
            for j in range(1, len(self.zsDst.kr)):
                self.forest_dist(self.zsSrc.kr[i], self.zsDst.kr[j])

        return self.treeDist

    def forest_dist(self, i, j):
        self.forestDist[self.zsSrc.lld(i) - 1][self.zsDst.lld(j) - 1] = 0
        for di in range(self.zsSrc.lld(i), i + 1):
            cost_del = self.get_deletion_cost(self.zsSrc.tree(di))
            self.forestDist[di][self.zsDst.lld(j) - 1] = self.forestDist[di - 1][self.zsDst.lld(j) - 1] + cost_del
            for dj in range(self.zsDst.lld(j), j + 1):
                cost_ins = self.get_insertion_cost(self.zsDst.tree(dj))
                self.forestDist[self.zsSrc.lld(i) - 1][dj] = self.forestDist[self.zsSrc.lld(i) - 1][dj - 1] + cost_ins
                if self.zsSrc.lld(di) == self.zsSrc.lld(i) and self.zsDst.lld(dj) == self.zsDst.lld(j):
                    cost_upd = self.get_update_cost(self.zsSrc.tree(di), self.zsDst.tree(dj))
                    self.forestDist[di][dj] = min(self.forestDist[di - 1][dj] + cost_del,
                                                  self.forestDist[di][dj - 1] + cost_ins,
                                                  self.forestDist[di - 1][dj - 1] + cost_upd)
                    self.treeDist[di][dj] = self.forestDist[di][dj]
                else:
                    self.forestDist[di][dj] = min(self.forestDist[di - 1][dj] + cost_del,
                                                  self.forestDist[di][dj - 1] + cost_ins,
                                                  self.forestDist[self.zsSrc.lld(di) - 1][self.zsDst.lld(dj) - 1] +
                                                  self.treeDist[di][dj])

    def _match(self):
        self.compute_tree_dist()

        root_node_pair = True
        tree_pairs = deque()

        tree_pairs.appendleft([self.zsSrc.node_count, self.zsDst.node_count])

        while tree_pairs:
            tree_pair = tree_pairs.popleft()
            last_row = tree_pair[0]
            last_col = tree_pair[1]

            if not root_node_pair:
                self.forest_dist(last_row, last_col)

            root_node_pair = False

            first_row = self.zsSrc.lld(last_row) - 1
            first_col = self.zsDst.lld(last_col) - 1

            row = last_row
            col = last_col

            while row > first_row or col > first_col:
                if row > first_row and self.forestDist[row - 1][col] + 1 == self.forestDist[row][col]:
                    row -= 1
                elif col > first_col and self.forestDist[row][col - 1] + 1 == self.forestDist[row][col]:
                    col -= 1
                else:
                    if self.zsSrc.lld(row) - 1 == self.zsSrc.lld(last_row) - 1 and self.zsDst.lld(
                            col) - 1 == self.zsDst.lld(last_col) - 1:
                        t_src = self.zsSrc.tree(row)
                        t_dst = self.zsDst.tree(col)
                        if t_src.type == t_dst.type:
                            self.mappings.add_mapping(t_src, t_dst)
                        else:
                            raise Exception("Should not map incompatible nodes.")
                        row -= 1
                        col -= 1
                    else:
                        tree_pairs.appendleft([row, col])
                        row = self.zsSrc.lld(row) - 1
                        col = self.zsDst.lld(col) - 1

    @staticmethod
    def get_deletion_cost(n):
        return 1

    @staticmethod
    def get_insertion_cost(n):
        return 1

    @staticmethod
    def get_update_cost(n1, n2):
        if n1.type == n2.type:
            if not n1.label or not n2.label:
                return 1
            else:
                return 1 - SequenceMatcher(None, n1.label, n2.label).ratio()  # TODO: q-gram distance
        else:
            return math.inf


class ZsTree:
    def __init__(self, t):
        self.node_count = t.get_metrics().size
        self.leaf_count = 0
        self.llds = [0 for _ in range(self.node_count)]
        self.labels = [None for _ in range(self.node_count)]
        self.kr = None

        idx = 1
        tmp_data = {}
        for n in t.post_order():
            tmp_data[n] = idx
            self.set_i_tree(idx, n)
            self.set_lld(idx, tmp_data[ZsMatcher.get_first_leaf(n)])
            if n.is_leaf:
                self.leaf_count += 1
            idx += 1

        self.set_key_roots()

    def set_i_tree(self, i, tree):
        self.labels[i - 1] = tree
        if self.node_count < i:
            self.node_count = i

    def set_lld(self, i, lld):
        self.llds[i - 1] = lld - 1
        if self.node_count < i:
            self.node_count = i

    def is_leaf(self, i):
        return self.lld(i) == i

    def lld(self, i):
        return self.llds[i - 1] + 1

    def tree(self, i):
        return self.labels[i - 1]

    def set_key_roots(self):
        self.kr = [0 for _ in range(self.leaf_count + 1)]
        visited = [False for _ in range(self.node_count + 1)]
        k = len(self.kr) - 1
        for i in range(self.node_count, 0, -1):
            if not visited[self.lld(i)]:
                self.kr[k] = i
                visited[self.lld(i)] = True
                k -= 1
