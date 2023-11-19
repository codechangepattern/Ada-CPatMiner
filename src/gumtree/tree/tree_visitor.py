from abc import ABC, abstractmethod
from collections import deque


class TreeVisitor(ABC):
    """
    Interface for AST visitors.
    """

    @staticmethod
    def visit_tree(root, visitor):
        """
        Start visiting the given tree using the provided visitor.
        The tree is visited in post-order.
        """
        stack = deque()
        stack.append((root, iter(root.get_children())))
        visitor.start_tree(root)

        while stack:
            tree, it = stack[-1]

            try:
                child = next(it)
                stack.append((child, iter(child.get_children())))
                visitor.start_tree(child)
            except StopIteration:
                visitor.end_tree(tree)
                stack.pop()

    @abstractmethod
    def start_tree(self, tree):
        """
        Callback executed when entering a node during the visit.
        The visited node is provided as a parameter of the callback.
        """
        pass

    @abstractmethod
    def end_tree(self, tree):
        """
        Callback executed when exiting a node during the visit.
        The visited node is provided as a parameter of the callback.
        """
        pass


class DefaultTreeVisitor(TreeVisitor):
    """
    A default does nothing visitor.
    """

    def start_tree(self, tree):
        pass

    def end_tree(self, tree):
        pass


class InnerNodesAndLeavesVisitor(TreeVisitor):
    """
    A does nothing visitor that distinguished between visiting an inner node
    and visiting a leaf node.
    """

    def start_tree(self, tree):
        if tree.is_leaf():
            self.visit_leaf(tree)
        else:
            self.start_inner_node(tree)

    def end_tree(self, tree):
        if not tree.is_leaf():
            self.end_inner_node(tree)

    def start_inner_node(self, tree):
        pass

    def visit_leaf(self, tree):
        pass

    def end_inner_node(self, tree):
        pass
