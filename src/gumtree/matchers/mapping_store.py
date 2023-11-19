from collections import namedtuple


Pair = namedtuple('Pair', ['first', 'second'])


class Mapping(Pair):

    def __str__(self):
        return f"{self.first} -> {self.second}"


class MappingStore:
    def __init__(self, src, dst):
        self.src = src
        self.dst = dst
        self.src_to_dst = {}
        self.dst_to_src = {}

    def __iter__(self):
        return iter(self.as_set())

    def __str__(self):
        return '\n'.join(str(m) for m in self)

    def size(self):
        return len(self.src_to_dst)

    def as_set(self):
        return {Mapping(src, self.src_to_dst[src]) for src in self.src_to_dst}

    def add_mapping(self, src, dst):
        self.src_to_dst[src] = dst
        self.dst_to_src[dst] = src

    def add_mapping_recursively(self, src, dst):
        self.add_mapping(src, dst)
        for child_src, child_dst in zip(src.children, dst.children):
            self.add_mapping_recursively(child_src, child_dst)

    def remove_mapping(self, src, dst):
        del self.src_to_dst[src]
        del self.dst_to_src[dst]

    def get_dst_for_src(self, src):
        return self.src_to_dst.get(src)

    def get_src_for_dst(self, dst):
        return self.dst_to_src.get(dst)

    def is_src_mapped(self, src):
        return src in self.src_to_dst

    def is_dst_mapped(self, dst):
        return dst in self.dst_to_src

    def are_both_unmapped(self, src, dst):
        return not self.is_src_mapped(src) and not self.is_dst_mapped(dst)

    def are_srcs_unmapped(self, srcs):
        return all(not self.is_src_mapped(src) for src in srcs)

    def are_dsts_unmapped(self, dsts):
        return all(not self.is_dst_mapped(dst) for dst in dsts)

    def has_unmapped_src_children(self, t):
        return any(not self.is_src_mapped(c) for c in t.get_descendants())

    def has_unmapped_dst_children(self, t):
        return any(not self.is_dst_mapped(c) for c in t.get_descendants())

    def has(self, src, dst):
        return self.src_to_dst.get(src) == dst

    def is_mapping_allowed(self, src, dst):
        return src.has_same_type(dst) and self.are_both_unmapped(src, dst)
