from gumtree.gen.ada_tree_visitor import AdaTreeVisitor
from gumtree.tree.tree_context import TreeContext
from utils.ada_node_visitor import accept


class AdaTreeGenerator:
    def generate(self, root, source) -> TreeContext:
        visitor = AdaTreeVisitor(root, source)
        accept(root, visitor)
        return visitor.get_tree_context()
