from gumtree.matchers.configuration_options import ConfigurationOptions
from gumtree.matchers.mapping_store import MappingStore
from gumtree.matchers.optimal.zs.zs_matcher import ZsMatcher
from gumtree.matchers.similarity_metrics import SimilarityMetrics


class GreedyBottomUpMatcher:
    DEFAULT_SIZE_THRESHOLD = 1000
    DEFAULT_SIM_THRESHOLD = 0.5

    def __init__(self):
        self.size_threshold = self.DEFAULT_SIZE_THRESHOLD
        self.sim_threshold = self.DEFAULT_SIM_THRESHOLD

    def configure(self, properties):
        self.size_threshold = properties.tryConfigure(ConfigurationOptions.bu_minsize, self.size_threshold)
        self.sim_threshold = properties.tryConfigure(ConfigurationOptions.bu_minsim, self.sim_threshold)

    def match(self, src, dst, mappings):
        for t in src.post_order():
            if t.is_root():
                mappings.add_mapping(t, dst)
                self.last_chance_match(mappings, t, dst)
                break
            elif not (mappings.is_src_mapped(t) or t.is_leaf()):
                candidates = self.get_dst_candidates(mappings, t)
                best = None
                max = -1
                for cand in candidates:
                    sim = SimilarityMetrics.dice_similarity(t, cand, mappings)
                    if sim > max and sim >= self.sim_threshold:
                        max = sim
                        best = cand
                if best is not None:
                    self.last_chance_match(mappings, t, best)
                    mappings.add_mapping(t, best)
        return mappings

    @staticmethod
    def get_dst_candidates(mappings, src):
        seeds = [mappings.get_dst_for_src(c) for c in src.get_descendants() if mappings.is_src_mapped(c)]
        candidates = []
        visited = set()
        for seed in seeds:
            while seed.get_parent() is not None:
                parent = seed.get_parent()
                if parent in visited:
                    break
                visited.add(parent)
                if parent.get_type() == src.get_type() and not (mappings.is_dst_mapped(parent) or parent.is_root()):
                    candidates.append(parent)
                seed = parent
        return candidates

    def last_chance_match(self, mappings, src, dst):
        if src.get_metrics().size < self.size_threshold or dst.get_metrics().size < self.size_threshold:
            m = ZsMatcher()
            zs_mappings = m.match(src, dst, MappingStore(src, dst))
            for candidate in zs_mappings:
                src_cand = candidate.first
                dst_cand = candidate.second
                if mappings.is_mapping_allowed(src_cand, dst_cand):
                    mappings.add_mapping(src_cand, dst_cand)

    def get_size_threshold(self):
        return self.size_threshold

    def set_size_threshold(self, size_threshold):
        self.size_threshold = size_threshold

    def get_sim_threshold(self):
        return self.sim_threshold

    def setSimThreshold(self, sim_threshold):
        self.sim_threshold = sim_threshold

    @staticmethod
    def get_applicable_options():
        return {ConfigurationOptions.bu_minsize, ConfigurationOptions.bu_minsim}
