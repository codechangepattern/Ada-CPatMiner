from functools import cmp_to_key
from operator import attrgetter

from gumtree.matchers.heuristic.gt.abstract_subtree_matcher import AbstractSubtreeMatcher
from gumtree.matchers.heuristic.gt.mapping_comparators import MappingComparators
from gumtree.matchers.mapping_store import Mapping


class GreedySubtreeMatcher(AbstractSubtreeMatcher):
    def __init__(self):
        super().__init__()

    def handle_ambiguous_mappings(self, ambiguous_mappings):
        comparator = MappingComparators.FullMappingComparator(self.mappings)

        ambiguous_mappings.sort(key=cmp_to_key(AmbiguousMappingsComparator.compare))

        for pair in ambiguous_mappings:
            candidates = self.convert_to_mappings(pair)
            candidates.sort(key=cmp_to_key(comparator.compare))

            for mapping in candidates:
                if self.mappings.are_both_unmapped(mapping.first, mapping.second):
                    self.mappings.add_mapping_recursively(mapping.first, mapping.second)

    @staticmethod
    def convert_to_mappings(ambiguous_mapping):
        mappings = []
        for src in ambiguous_mapping.first:
            for dst in ambiguous_mapping.second:
                mappings.append(Mapping(src, dst))
        return mappings


class AmbiguousMappingsComparator:
    @staticmethod
    def compare(m1, m2):
        s1 = max(t.get_metrics().size for t in m1.first)
        s2 = max(t.get_metrics().size for t in m2.first)
        return s2 - s1
