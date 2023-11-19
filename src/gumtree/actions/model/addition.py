from gumtree.actions.model.action import Action


class Addition(Action):
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
            str(self.node),
            str(self.parent) if self.parent else "root",
            self.position
        )

    def __eq__(self, other):
        if not super().__eq__(other):
            return False

        return self.parent == other.parent and self.position == other.position

