from gumtree.actions.model.addition import Addition


class Insert(Addition):
    def __init__(self, node, parent, pos):
        super().__init__(node, parent, pos)

    def get_name(self):
        return "insert-node"
