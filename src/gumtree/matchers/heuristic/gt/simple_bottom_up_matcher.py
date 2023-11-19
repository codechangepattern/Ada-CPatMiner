from collections import defaultdict
import numpy as np

from gumtree.matchers.configuration_options import ConfigurationOptions
from gumtree.matchers.similarity_metrics import SimilarityMetrics
from gumtree.tree.tree_utils import TreeUtils
from gumtree.utils import sequence_algorithms


class SimpleBottomUpMatcher:
    DEFAULT_SIM_THRESHOLD = np.nan

    def __init__(self):
        self.sim_threshold = self.DEFAULT_SIM_THRESHOLD

    def configure(self, properties):
        self.sim_threshold = properties.try_configure(ConfigurationOptions.bu_minsim, self.sim_threshold)

    def match(self, src, dst, mappings):
        for t in src.post_order():
            if t.is_root():
                mappings.add_mapping(t, dst)
                self.last_chance_match(mappings, t, dst)
                break
            elif not (mappings.is_src_mapped(t) or t.is_leaf()):
                candidates = self.get_dst_candidates(mappings, t)
                best = None
                max_val = -1
                t_size = len(t.get_descendants())

                for candidate in candidates:
                    threshold = 1 / (1 + np.log(len(candidate.get_descendants()) + t_size)) if np.isnan(self.sim_threshold) else self.sim_threshold
                    sim = SimilarityMetrics.chawathe_similarity(t, candidate, mappings)
                    if sim > max_val and sim >= threshold:
                        max_val = sim
                        best = candidate

                if best is not None:
                    self.last_chance_match(mappings, t, best)
                    mappings.add_mapping(t, best)
            elif mappings.is_src_mapped(t) and mappings.has_unmapped_src_children(t) and mappings.has_unmapped_dst_children(mappings.get_dst_for_src(t)):
                self.last_chance_match(mappings, t, mappings.get_dst_for_src(t))
        return mappings

    @staticmethod
    def get_dst_candidates(mappings, src):
        seeds = [mappings.get_dst_for_src(c) for c in src.get_descendants() if mappings.get_dst_for_src(c) is not None]
        candidates = []
        visited = set()

        for seed in seeds:
            while seed.get_parent() is not None:
                parent = seed.get_parent()
                if parent in visited:
                    break
                visited.add(parent)
                if parent.get_type() == src.get_type() and not mappings.is_dst_mapped(parent) and not parent.is_root():
                    candidates.append(parent)
                seed = parent

        return candidates

    def last_chance_match(self, mappings, src, dst):
        self.lcs_equal_matching(mappings, src, dst)
        self.lcs_structure_matching(mappings, src, dst)
        self.histogram_matching(mappings, src, dst)

    @staticmethod
    def lcs_equal_matching(mappings, src, dst):
        unmapped_src_children = [c for c in src.children if not mappings.is_src_mapped(c)]
        unmapped_dst_children = [c for c in dst.children if not mappings.is_dst_mapped(c)]

        lcs = sequence_algorithms.longest_common_subsequence_with_isomorphism(unmapped_src_children,
                                                                              unmapped_dst_children)

        for x in lcs:
            t1 = unmapped_src_children[x[0]]
            t2 = unmapped_dst_children[x[1]]
            if mappings.are_srcs_unmapped(TreeUtils.pre_order(t1)) and mappings.are_dsts_unmapped(
                    TreeUtils.pre_order(t2)):
                mappings.add_mapping_recursively(t1, t2)

    @staticmethod
    def lcs_structure_matching(mappings, src, dst):
        unmapped_src_children = [c for c in src.children if not mappings.is_src_mapped(c)]
        unmapped_dst_children = [c for c in dst.children if not mappings.is_dst_mapped(c)]

        lcs = sequence_algorithms.longest_common_subsequence_with_isostructure(unmapped_src_children,
                                                                               unmapped_dst_children)

        for x in lcs:
            t1 = unmapped_src_children[x[0]]
            t2 = unmapped_dst_children[x[1]]
            if mappings.are_srcs_unmapped(TreeUtils.pre_order(t1)) and mappings.are_dsts_unmapped(
                    TreeUtils.pre_order(t2)):
                mappings.add_mapping_recursively(t1, t2)

    def histogram_matching(self, mappings, src, dst):
        src_histogram = defaultdict(list)
        for c in src.children:
            if not mappings.is_src_mapped(c):
                src_histogram[c.type].append(c)

        dst_histogram = defaultdict(list)
        for c in dst.children:
            if not mappings.is_dst_mapped(c):
                dst_histogram[c.type].append(c)

        for t in src_histogram.keys():
            if t in dst_histogram and len(src_histogram[t]) == 1 and len(dst_histogram[t]) == 1:
                src_child = src_histogram[t][0]
                dst_child = dst_histogram[t][0]
                mappings.add_mapping(src_child, dst_child)
                self.last_chance_match(mappings, src_child, dst_child)
