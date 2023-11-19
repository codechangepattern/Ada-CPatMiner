from gumtree.actions.model.tree_action import TreeAction


class TreeDelete(TreeAction):
    def __init__(self, node):
        super().__init__(node)

    def get_name(self):
        return "delete-tree"

    def __str__(self):
        return "===\n{}\n---\n{}".format(self.get_name(), self.node)
