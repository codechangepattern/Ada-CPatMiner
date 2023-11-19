from gumtree.matchers.mapping_store import MappingStore
from gumtree.matchers.optimal.zs.zs_matcher import ZsMatcher
import gumtree.utils.sequence_algorithms as sequence_algorithms
from gumtree.matchers.similarity_metrics import SimilarityMetrics
import math


class HybridBottomUpMatcher:
    DEFAULT_SIZE_THRESHOLD = 20
    DEFAULT_SIM_THRESHOLD = float('nan')

    def __init__(self):
        self.size_threshold = HybridBottomUpMatcher.DEFAULT_SIZE_THRESHOLD
        self.sim_threshold = HybridBottomUpMatcher.DEFAULT_SIM_THRESHOLD

    def configure(self, properties):
        self.size_threshold = properties.get('bu_minsize', self.size_threshold)
        self.sim_threshold = properties.get('bu_minsim', self.sim_threshold)

    def match(self, src, dst, mappings):
        for t in src.post_order():
            if t.is_root():
                mappings.add_mapping(t, dst)
                self.last_chance_match(mappings, t, dst)
                break
            elif not mappings.is_src_mapped(t) and not t.is_leaf():
                candidates = self.get_dst_candidates(mappings, t)
                best = None
                max_sim = -1.0
                t_size = len(t.get_descendants())

                for candidate in candidates:
                    threshold = 1.0 / (1.0 + math.log(len(candidate.get_descendants()) + t_size)) if math.isnan(
                        self.sim_threshold) else self.sim_threshold
                    sim = SimilarityMetrics.chawathe_similarity(t, candidate,
                                                   mappings)  # assumes a method to calculate Chawathe similarity
                    if sim > max_sim and sim >= threshold:
                        max_sim = sim
                        best = candidate

                if best:
                    self.last_chance_match(mappings, t, best)
                    mappings.add_mapping(t, best)
            elif mappings.is_src_mapped(t) and mappings.has_unmapped_src_children(
                    t) and mappings.has_unmapped_dst_children(mappings.get_dst_for_src(t)):
                self.last_chance_match(mappings, t, mappings.get_dst_for_src(t))
        return mappings

    def get_dst_candidates(self, mappings, src):
        seeds = [mappings.get_dst_for_src(c) for c in src.get_descendants() if mappings.get_dst_for_src(c)]
        candidates = set()
        for seed in seeds:
            while seed.parent:
                parent = seed.parent
                if parent in candidates:
                    break
                if parent.type == src.type and not mappings.is_dst_mapped(parent) and not parent.is_root():
                    candidates.add(parent)
                seed = parent
        return list(candidates)

    def last_chance_match(self, mappings, src, dst):
        if src.get_metrics().size < self.size_threshold or dst.get_metrics().size < self.size_threshold:
            self.optimal_last_chance_match(mappings, src, dst)
        else:
            self.simple_last_chance_match(mappings, src, dst)

    def optimal_last_chance_match(self, mappings, src, dst):
        m = ZsMatcher()
        zs_mappings = m.match(src, dst, MappingStore(src, dst))
        for src_cand, dst_cand in zs_mappings:
            if mappings.is_mapping_allowed(src_cand, dst_cand):
                mappings.add_mapping_recursively(src_cand, dst_cand)

    def simple_last_chance_match(self, mappings, src, dst):
        self.lcs_equal_matching(mappings, src, dst)
        self.lcs_structure_matching(mappings, src, dst)
        if src.is_root() and dst.is_root():
            self.histogram_matching(mappings, src, dst)
        elif not (src.is_root() or dst.is_root()) and src.parent.type == dst.parent.type:
            self.histogram_matching(mappings, src, dst)

    def lcs_equal_matching(self, mappings, src, dst):
        src_children = src.children
        dst_children = dst.children
        lcs = sequence_algorithms.longest_common_subsequence_with_isomorphism(src_children, dst_children)
        for x, y in lcs:
            t1 = src_children[x]
            t2 = dst_children[y]
            if mappings.are_srcs_unmapped(t1.pre_order()) and mappings.are_dsts_unmapped(t2.pre_order()):
                mappings.add_mapping_recursively(t1, t2)

    def lcs_structure_matching(self, mappings, src, dst):
        src_children = src.children
        dst_children = dst.children
        lcs = sequence_algorithms.longest_common_subsequence_with_isostructure(src_children, dst_children)
        for x, y in lcs:
            t1 = src_children[x]
            t2 = dst_children[y]
            if mappings.are_srcs_unmapped(t1.pre_order()) and mappings.are_dsts_unmapped(t2.pre_order()):
                mappings.add_mapping_recursively(t1, t2)

    def histogram_matching(self, mappings, src, dst):
        src_children = src.children
        dst_children = dst.children

        src_histogram = {}
        for c in src_children:
            src_histogram.setdefault(c.type, []).append(c)

        dst_histogram = {}
        for c in dst_children:
            dst_histogram.setdefault(c.type, []).append(c)

        for t, trees in src_histogram.items():
            if t in dst_histogram and len(trees) == 1 and len(dst_histogram[t]) == 1:
                t1 = trees[0]
                t2 = dst_histogram[t][0]
                if mappings.are_both_unmapped(t1, t2):
                    mappings.add_mapping(t1, t2)
                    self.last_chance_match(mappings, t1, t2)

    def get_applicable_options(self):
        return {'bu_minsize'}
