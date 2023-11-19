from typing import List, Dict, Tuple, Set
from collections import defaultdict

import numpy as np

from gumtree.matchers.similarity_metrics import SimilarityMetrics
from gumtree.utils import sequence_algorithms


class Mapping:
    def __init__(self, first, second):
        self.first = first
        self.second = second


class MappingComparators:

    class FullMappingComparator:
        def __init__(self, ms):
            self.siblings_comparator = MappingComparators.SiblingsSimilarityMappingComparator(ms)
            self.parents_comparator = MappingComparators.ParentsSimilarityMappingComparator()
            self.parents_position_comparator = MappingComparators.PositionInParentsSimilarityMappingComparator()
            self.textual_position_comparator = MappingComparators.TextualPositionDistanceMappingComparator()
            self.position_comparator = MappingComparators.AbsolutePositionDistanceMappingComparator()

        def compare(self, m1, m2):
            result = self.siblings_comparator.compare(m1, m2)
            if result != 0:
                return result

            result = self.parents_comparator.compare(m1, m2)
            if result != 0:
                return result

            result = self.parents_position_comparator.compare(m1, m2)
            if result != 0:
                return result

            result = self.textual_position_comparator.compare(m1, m2)
            if result != 0:
                return result

            return self.position_comparator.compare(m1, m2)

    class SiblingsSimilarityMappingComparator:
        def __init__(self, ms):
            self.ms = ms
            self.src_descendants = defaultdict(set)
            self.dst_descendants = defaultdict(set)
            self.cached_similarities = {}

        def compare(self, m1, m2):
            if m1.first.parent == m2.first.parent and m1.second.parent == m2.second.parent:
                return 0

            if m1 not in self.cached_similarities:
                sim = SimilarityMetrics.dice_coefficient(self.common_descendants_nb(m1.first.parent, m1.second.parent),
                                                         len(self.src_descendants[m1.first.parent]),
                                                         len(self.dst_descendants[m1.second.parent]))
                self.cached_similarities[m1] = sim

            if m2 not in self.cached_similarities:
                sim = SimilarityMetrics.dice_coefficient(self.common_descendants_nb(m2.first.parent, m2.second.parent),
                                                         len(self.src_descendants[m2.first.parent]),
                                                         len(self.dst_descendants[m2.second.parent]))
                self.cached_similarities[m2] = sim

            return self.cached_similarities[m2] - self.cached_similarities[m1]

        def common_descendants_nb(self, src, dst):
            self.src_descendants[src] = set(src.get_descendants())
            self.dst_descendants[dst] = set(dst.get_descendants())

            common = 0
            for t in self.src_descendants[src]:
                mapped = self.ms.get_dst_for_src(t)
                if mapped and mapped in self.dst_descendants[dst]:
                    common += 1

            return common

    class ParentsSimilarityMappingComparator:
        def __init__(self):
            self.src_ancestors = {}
            self.dst_ancestors = {}
            self.cached_similarities = {}

        def compare(self, m1, m2):
            if m1.first.parent == m2.first.parent and m1.second.parent == m2.second.parent:
                return 0

            self.src_ancestors.setdefault(m1.first, m1.first.get_parents())
            self.dst_ancestors.setdefault(m1.second, m1.second.get_parents())
            self.src_ancestors.setdefault(m2.first, m2.first.get_parents())
            self.dst_ancestors.setdefault(m2.second, m2.second.get_parents())

            if m1 not in self.cached_similarities:
                m1_sim = SimilarityMetrics.dice_coefficient(
                    self.common_parents_nb(m1.first, m1.second),
                    len(self.src_ancestors[m1.first]),
                    len(self.dst_ancestors[m1.second])
                )
                self.cached_similarities[m1] = m1_sim

            if m2 not in self.cached_similarities:
                m2_sim = SimilarityMetrics.dice_coefficient(
                    self.common_parents_nb(m2.first, m2.second),
                    len(self.src_ancestors[m2.first]),
                    len(self.dst_ancestors[m2.second])
                )
                self.cached_similarities[m2] = m2_sim

            return self.cached_similarities[m2] - self.cached_similarities[m1]

        def common_parents_nb(self, src, dst):
            return len(sequence_algorithms.longest_common_subsequence_with_type(
                self.src_ancestors[src],
                self.dst_ancestors[dst]
            ))

    class PositionInParentsSimilarityMappingComparator:
        @classmethod
        def compare(cls, m1, m2):
            m1_distance = cls.distance(m1)
            m2_distance = cls.distance(m2)
            return m1_distance - m2_distance

        @classmethod
        def distance(cls, m):
            pos_vector1 = cls.pos_vector(m.first)
            pos_vector2 = cls.pos_vector(m.second)
            min_length = min(len(pos_vector1), len(pos_vector2))
            sum_squares = sum((pos_vector1[i] - pos_vector2[i]) ** 2 for i in range(min_length))
            return np.sqrt(sum_squares)

        @staticmethod
        def pos_vector(src):
            pos_vector = []
            current = src
            while current is not None and current.parent is not None:
                parent = current.parent
                pos = parent.get_child_position(current)
                pos_vector.append(pos)
                current = parent
            return pos_vector

    class TextualPositionDistanceMappingComparator:
        def compare(self, m1, m2):
            m1_pos_dist = abs(m1.first.pos - m2.first.pos) + abs(m1.first.get_end_pos() - m2.first.get_end_pos())
            m2_pos_dist = abs(m2.first.pos - m2.second.pos) + abs(m2.first.get_end_pos() - m2.second.get_end_pos())
            return m1_pos_dist - m2_pos_dist

    class AbsolutePositionDistanceMappingComparator:
        def compare(self, m1, m2):
            m1_pos_dist = abs(m1.first.metrics.position - m2.first.metrics.position)
            m2_pos_dist = abs(m2.first.metrics.position - m2.second.metrics.position)
            return m1_pos_dist - m2_pos_dist
