from libadalang import AdaNode, CompilationUnit, Identifier, StringLiteral, IntLiteral, RealLiteral, SubpBody
from overrides import overrides

from gumtree.tree.tree import Tree
from gumtree.tree.tree_context import TreeContext
from gumtree.tree.type import TypeSet
from utils.ada_node_visitor import AdaNodeVisitor


class AdaTreeVisitor(AdaNodeVisitor):
    def __init__(self, root, source):
        self.trees = {}
        self.context = TreeContext()
        self.context.set_source(source)
        tree = self.build_tree(root)
        self.context.set_root(tree)
        self.context.set_trees(self.trees)

    def get_tree_context(self) -> TreeContext:
        return self.context

    @overrides
    def visit(self, node: AdaNode) -> bool:
        if isinstance(node, CompilationUnit):
            return True
        elif isinstance(node, SubpBody) and len(self.trees) == 1:
            return True
        else:
            tree = self.build_tree(node)
            parent = self.trees[node.parent]
            parent.add_child(tree)

            if isinstance(node, Identifier):
                tree.set_label(node.text)
            elif isinstance(node, StringLiteral):
                tree.set_label(node.p_denoted_value)
            elif isinstance(node, IntLiteral):
                tree.set_label(node.text)
            elif isinstance(node, RealLiteral):
                tree.set_label(node.text)

        return True

    def get_absolute_position(self, node: AdaNode):
        # Split the source code into lines
        lines = self.context.get_source().splitlines()

        # Calculate the position up to the start line
        absolute_position = sum(len(line) + 1 for line in lines[:node.sloc_range.start.line - 1])  # +1 for newline characters

        # Add the column offset to the position
        absolute_position += node.sloc_range.start.column - 1
        return absolute_position

    def build_tree(self, node: AdaNode) -> Tree:
        tree = self.context.create_tree(TypeSet.type(type(node).__name__), Tree.NO_LABEL)
        tree.ast = node
        tree.set_pos(self.get_absolute_position(node))
        tree.set_length(len(node.text))
        self.trees[node] = tree
        return tree
