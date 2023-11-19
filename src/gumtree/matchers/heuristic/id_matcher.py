from gumtree.tree.tree import Tree
from gumtree.tree.tree_utils import TreeUtils


class IdMatcher:

    def match(self, src: Tree, dst: Tree, mappings) -> "MappingStore":
        src_candidate_mappings = self._create_candidate_mappings(src)
        dst_candidate_mappings = self._create_candidate_mappings(dst)

        for id_, src_trees in src_candidate_mappings.items():
            if len(src_trees) == 1:
                dst_tree = dst_candidate_mappings.get(id_)
                if dst_tree and len(dst_tree) == 1:
                    mappings.add_mapping(src_trees.pop(), dst_tree.pop())

        return mappings

    def _create_candidate_mappings(self, tree: Tree) -> dict:
        candidate_mappings = {}
        for t in TreeUtils.pre_order(tree):
            id_ = t.get_metadata("id")
            if id_:
                if id_ not in candidate_mappings:
                    candidate_mappings[id_] = set()
                candidate_mappings[id_].add(t)
        return candidate_mappings
