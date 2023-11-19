from gumtree.actions.model.tree_addition import TreeAddition


class TreeInsert(TreeAddition):
    def __init__(self, node, parent, pos):
        super().__init__(node, parent, pos)

    def get_name(self):
        return "insert-tree"
