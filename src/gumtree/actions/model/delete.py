from gumtree.actions.model.action import Action


class Delete(Action):
    def __init__(self, node):
        super().__init__(node)

    def get_name(self):
        return "delete-node"

    def __str__(self):
        return "===\n{}\n---\n{}\n===".format(self.get_name(), str(self.node))
