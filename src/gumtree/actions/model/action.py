class Action:
    def __init__(self, node):
        self.node = node

    @property
    def node(self):
        return self._node

    @node.setter
    def node(self, value):
        self._node = value

    def get_name(self):
        raise NotImplementedError("The 'get_name' method should be implemented in subclasses")

    def __eq__(self, other):
        if self is other:
            return True
        if other is None:
            return False
        if type(self) != type(other):
            return False

        return self.node == other.node
