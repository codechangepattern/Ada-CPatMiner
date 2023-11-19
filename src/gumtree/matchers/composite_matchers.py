from overrides import overrides

from gumtree.matchers.configurable_matcher import ConfigurableMatcher
from gumtree.matchers.heuristic.gt import GreedyBottomUpMatcher, GreedySubtreeMatcher, SimpleBottomUpMatcher, HybridBottomUpMatcher
from gumtree.matchers.heuristic.id_matcher import IdMatcher
from gumtree.matchers.mapping_store import MappingStore


class CompositeMatcher(ConfigurableMatcher):
    def __init__(self, matchers):
        self.matchers = matchers

    @overrides
    def match(self, src, dst, mappings=None):
        if mappings is None:
            mappings = MappingStore(src, dst)
        for matcher in self.matchers:
            mappings = matcher.match(src, dst, mappings)
        return mappings

    @overrides
    def configure(self, properties):
        for matcher in self.matchers:
            matcher.configure(properties)

    def matchers(self):
        return self.matchers

    @overrides
    def get_applicable_options(self):
        all_options = set()
        for matcher in self.matchers:
            all_options.update(matcher.applicable_options())
        return all_options


class ClassicGumtree(CompositeMatcher):
    def __init__(self):
        super().__init__([GreedySubtreeMatcher(), GreedyBottomUpMatcher()])


class SimpleGumtree(CompositeMatcher):
    def __init__(self):
        super().__init__([GreedySubtreeMatcher(), SimpleBottomUpMatcher()])


class SimpleIdGumTree(CompositeMatcher):
    def __init__(self):
        super().__init__([IdMatcher(), GreedySubtreeMatcher(), SimpleBottomUpMatcher()])


class HybridGumtree(CompositeMatcher):
    def __init__(self):
        super().__init__([GreedySubtreeMatcher(), HybridBottomUpMatcher()])

# ... more classes like ClassicGumtree and SimpleGumtree


# Registry of all matchers
MATCHERS = {
    "gumtree": ClassicGumtree(),
    "gumtree-simple": SimpleGumtree(),
    "gumtree-simple-id": SimpleIdGumTree(),
    "gumtree-hybrid": HybridGumtree()
    # ... more matchers
}
