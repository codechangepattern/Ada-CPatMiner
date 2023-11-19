from collections import defaultdict
from typing import Callable

from gumtree.matchers.heuristic.gt.priority_tree_queue import PriorityTreeQueue


class DefaultPriorityTreeQueue(PriorityTreeQueue):

    def __init__(self, root, minimum_priority, priority_calculator):
        self.trees = defaultdict(list)
        self.minimum_priority = minimum_priority
        self.priority_calculator = priority_calculator
        self.add(root)

    def pop_open(self):
        pop = self.pop()
        for t in pop:
            self.open(t)
        return pop

    def set_priority_calculator(self, priority_calculator: Callable):
        self.priority_calculator = priority_calculator

    def pop(self):
        return self.trees.pop(self.current_priority())

    def open(self, tree):
        for c in tree.get_children():
            self.add(c)

    def current_priority(self):
        return max(self.trees.keys())

    def set_minimum_priority(self, minimum_priority: int):
        self.minimum_priority = minimum_priority

    def get_minimum_priority(self) -> int:
        return self.minimum_priority

    def is_empty(self):
        return len(self.trees) == 0

    def clear(self):
        self.trees.clear()

    def add(self, t):
        priority = self.priority_calculator(t)
        if priority < int(self.get_minimum_priority()):
            return

        self.trees[priority].append(t)
