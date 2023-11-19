from abc import ABC, abstractmethod

from gumtree.matchers.configuration_options import ConfigurationOptions
from gumtree.matchers.heuristic.gt.default_priority_tree_queue import DefaultPriorityTreeQueue
from gumtree.matchers.heuristic.gt.hash_based_mapper import HashBasedMapper
from gumtree.matchers.heuristic.gt.priority_tree_queue import PriorityTreeQueue
from gumtree.matchers.mapping_store import MappingStore
from gumtree.matchers.matcher import Matcher


class AbstractSubtreeMatcher(Matcher, ABC):
    DEFAULT_MIN_PRIORITY: int = 1
    DEFAULT_PRIORITY_CALCULATOR = 'height'

    def __init__(self):
        self.min_priority: int = self.DEFAULT_MIN_PRIORITY
        self.priority_calculator = PriorityTreeQueue.get_priority_calculator(self.DEFAULT_PRIORITY_CALCULATOR)
        self.src = None
        self.dst = None
        self.mappings = None

    def configure(self, properties):
        self.min_priority = properties.try_configure(ConfigurationOptions.st_minprio, self.min_priority)
        self.priority_calculator = PriorityTreeQueue.get_priority_calculator(
            properties.try_configure(ConfigurationOptions.st_priocalc, self.DEFAULT_PRIORITY_CALCULATOR))

    def match(self, src, dst, mappings=None):
        if mappings is None:
            mappings = MappingStore(src, dst)

        self.src = src
        self.dst = dst
        self.mappings = mappings

        ambiguous_mappings = []

        src_trees = DefaultPriorityTreeQueue(src, self.min_priority, self.priority_calculator)
        dst_trees = DefaultPriorityTreeQueue(dst, self.min_priority, self.priority_calculator)

        while PriorityTreeQueue.synchronize(src_trees, dst_trees):
            local_hash_mappings = HashBasedMapper()
            local_hash_mappings.add_srcs(src_trees.pop())
            local_hash_mappings.add_dsts(dst_trees.pop())

            for pair in local_hash_mappings.unique():
                first_tree = next(iter(pair.first))
                second_tree = next(iter(pair.second))
                mappings.add_mapping_recursively(first_tree, second_tree)

            for pair in local_hash_mappings.ambiguous():
                ambiguous_mappings.append(pair)

            for pair in local_hash_mappings.unmapped():
                for tree in pair.first:
                    src_trees.open(tree)
                for tree in pair.second:
                    dst_trees.open(tree)

        self.handle_ambiguous_mappings(ambiguous_mappings)
        return self.mappings

    @abstractmethod
    def handle_ambiguous_mappings(self, ambiguous_mappings):
        pass

    def get_min_priority(self):
        return self.min_priority

    def set_min_priority(self, min_priority):
        self.min_priority = min_priority

    def get_applicable_options(self):
        return {ConfigurationOptions.st_priocalc, ConfigurationOptions.st_minprio}
