class EditScript:
    def __init__(self):
        """
        Instantiate a new edit script.
        """
        self.actions = []

    def __iter__(self):
        """
        Allows iteration over the actions.
        """
        return iter(self.actions)

    def add(self, action, index=None):
        """
        Add an action to the script.
        If an index is provided, the action is inserted at the specified index.
        """
        if index is None:
            self.actions.append(action)
        else:
            self.actions.insert(index, action)

    def get(self, index):
        """
        Return the action at the given index.
        """
        return self.actions[index]

    def size(self):
        """
        Return the number of actions.
        """
        return len(self.actions)

    def remove(self, action_or_index):
        """
        Remove the provided action or action at the provided index from the script.
        """
        if isinstance(action_or_index, int):
            return self.actions.pop(action_or_index)
        else:
            self.actions.remove(action_or_index)
            return True

    def as_list(self):
        """
        Convert the edit script to a list of actions.
        """
        return self.actions

    def last_index_of(self, action):
        """
        Return the index of the last occurrence of the action in the script.
        """
        return len(self.actions) - 1 - self.actions[::-1].index(action)

