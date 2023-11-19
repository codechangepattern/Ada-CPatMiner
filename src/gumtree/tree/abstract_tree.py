from gumtree.tree.tree import Tree
from gumtree.tree.tree_metric_computer import TreeMetricComputer
from gumtree.tree.tree_visitor import TreeVisitor


class AbstractTree(Tree):

    def __init__(self):
        self.parent = None
        self.children = []
        self.metrics = None

    def __str__(self):
        if self.has_label():
            return f"{self.get_type()}: {self.get_label()} [{self.get_pos()}, {self.get_end_pos()}]"
        else:
            return f"{self.get_type()} [{self.get_pos()}, {self.get_end_pos()}]"

    def to_tree_string(self):
        return to_short_text(self)

    def get_parent(self):
        return self.parent

    def set_parent(self, parent):
        self.parent = parent

    def set_parent_and_update_children(self, parent):
        if self.parent:
            self.parent.get_children().remove(self)
        self.parent = parent
        if self.parent:
            parent.get_children().append(self)

    def get_children(self):
        return self.children

    def set_children(self, children):
        self.children = children
        for child in children:
            child.set_parent(self)

    def add_child(self, t):
        self.children.append(t)
        t.set_parent(self)

    def insert_child(self, t, position):
        self.children.insert(position, t)
        t.set_parent(self)

    def get_metrics(self):
        if not self.metrics:
            root = self
            if not self.is_root():
                parents = self.get_parents()
                root = parents[-1]
            TreeVisitor.visit_tree(root, TreeMetricComputer())
        return self.metrics

    def set_metrics(self, metrics):
        self.metrics = metrics


class EmptyEntryIterator:

    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration
