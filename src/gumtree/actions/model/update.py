from gumtree.actions.model.action import Action


class Update(Action):
    def __init__(self, node, value):
        super().__init__(node)
        self._value = value

    def get_name(self):
        return "update-node"

    def get_value(self):
        return self._value

    def __str__(self):
        return f"===\n{self.get_name()}\n---\n{self.node}\nreplace {self.node.get_label()} by {self.get_value()}"

    def __eq__(self, other):
        if not super().__eq__(other):
            return False
        return self._value == other.get_value()
