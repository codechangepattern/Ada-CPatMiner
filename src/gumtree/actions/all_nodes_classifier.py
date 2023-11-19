from gumtree.actions.abstract_i_tree_classifier import AbstractITreeClassifier
from gumtree.actions.model.delete import Delete
from gumtree.actions.model.insert import Insert
from gumtree.actions.model.move import Move
from gumtree.actions.model.tree_delete import TreeDelete
from gumtree.actions.model.tree_insert import TreeInsert
from gumtree.actions.model.update import Update


class AllNodesClassifier(AbstractITreeClassifier):
    def __init__(self, diff):
        super().__init__(diff)

    def classify(self):
        for action in self.diff.edit_script:
            if isinstance(action, Delete):
                self.src_del_trees.add(action.node)
            elif isinstance(action, TreeDelete):
                self.src_del_trees.add(action.node)
                self.src_del_trees.update(action.node.get_descendants())
            elif isinstance(action, Insert):
                self.dst_add_trees.add(action.node)
            elif isinstance(action, TreeInsert):
                self.dst_add_trees.add(action.node)
                self.dst_add_trees.update(action.node.get_descendants())
            elif isinstance(action, Update):
                self.src_upd_trees.add(action.node)
                self.dst_upd_trees.add(self.diff.mappings.get_dst_for_src(action.node))
            elif isinstance(action, Move):
                self.src_mv_trees.add(action.node)
                self.src_mv_trees.update(action.node.get_descendants())
                self.dst_mv_trees.add(self.diff.mappings.get_dst_for_src(action.node))
                self.dst_mv_trees.update(self.diff.mappings.get_dst_for_src(action.node).get_descendants())
