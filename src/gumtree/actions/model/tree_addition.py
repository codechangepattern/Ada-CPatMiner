from gumtree.actions.model.tree_action import TreeAction


class TreeAddition(TreeAction):
    def __init__(self, node, parent, pos):
        super().__init__(node)
        self.parent = parent
        self.position = pos

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value

    def __str__(self):
        return "===\n{}\n---\n{}\nto\n{}\nat {}".format(
            self.get_name(),
            self.node,
            self.parent if self.parent is not None else "root",
            self.position
        )

    def __eq__(self, other):
        if not super().__eq__(other):
            return False
        return self.parent == other.parent and self.position == other.position
