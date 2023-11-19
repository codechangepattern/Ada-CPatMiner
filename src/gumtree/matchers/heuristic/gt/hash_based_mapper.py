from collections import defaultdict, namedtuple

from gumtree.matchers.mapping_store import Pair


class HashBasedMapper:
    def __init__(self):
        self.mappings = defaultdict(lambda: Pair(set(), set()))

    def add_srcs(self, srcs):
        for t in srcs:
            self.add_src(t)

    def add_dsts(self, dsts):
        for t in dsts:
            self.add_dst(t)

    def add_src(self, src):
        pair = self.mappings.setdefault(src.get_metrics().hash, Pair(set(), set()))
        pair.first.add(src)

    def add_dst(self, dst):
        pair = self.mappings.setdefault(dst.get_metrics().hash, Pair(set(), set()))
        pair.second.add(dst)

    def unique(self):
        return [pair for pair in self.mappings.values() if len(pair.first) == 1 and len(pair.second) == 1]

    def ambiguous(self):
        return [pair for pair in self.mappings.values() if (len(pair.first) > 1 and len(pair.second) >= 1) or (len(pair.first) >= 1 and len(pair.second) > 1)]

    def unmapped(self):
        return [pair for pair in self.mappings.values() if len(pair.first) == 0 or len(pair.second) == 0]

    def is_src_mapped(self, src):
        return len(self.mappings[src.get_metrics().hash].second) > 0

    def is_dst_mapped(self, dst):
        return len(self.mappings[dst.get_metrics().hash].first) > 0
