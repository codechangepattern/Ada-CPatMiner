from gumtree.actions.model.tree_addition import TreeAddition


class Move(TreeAddition):  # Using Addition for now, replace with TreeAddition if it's different
    def __init__(self, node, parent, pos):
        super().__init__(node, parent, pos)

    def get_name(self):
        return "move-tree"
