from enum import Enum

from libadalang import BinOp

from gumtree.actions.diff import Diff
from gumtree.gen.ada_tree_generator import AdaTreeGenerator


class GumTree:
    class STATUS(Enum):
        UNCHANGED = 0
        CHANGED = 1
        INSERTED = 2
        DELETED = 3
        MOVED = 4
        UPDATED = 5

    def __init__(self, src_root, src_source, dst_root, dst_source):
        self.diff = Diff.compute(src_root, src_source, dst_root, dst_source, AdaTreeGenerator())
        self.classifier = self.diff.create_all_node_classifier()
        self.changed_nodes = set()
        self._apply_actions()

    @property
    def mappings(self):
        return self.diff.mappings

    def is_node_changed(self, node):
        if node in self.changed_nodes:
            return True

        if isinstance(node, BinOp):
            return self.is_node_changed(node.f_op)

        return False

    @property
    def deletions(self):
        return len(self.classifier.src_del_trees)

    def _apply_actions(self):
        changed_nodes = set().union(self.classifier.src_del_trees,
                                    self.classifier.src_mv_trees,
                                    self.classifier.src_upd_trees,
                                    self.classifier.dst_add_trees,
                                    self.classifier.dst_mv_trees,
                                    self.classifier.dst_upd_trees)
        changed_nodes = [node.ast for node in changed_nodes]
        self.changed_nodes = set(changed_nodes)






