from __future__ import annotations

from libadalang import AdaNode


def accept(node: AdaNode, visitor: AdaNodeVisitor):
    visitor.pre_visit(node)
    if visitor.visit(node):
        for child in node.children:
            if child is not None:
                accept(child, visitor)
    visitor.post_visit(node)


class AdaNodeVisitor:

    def pre_visit(self, node: AdaNode):
        pass

    def visit(self, node: AdaNode) -> bool:
        # print('Visitor visit: {}'.format(node))
        return True

    def post_visit(self, node: AdaNode):
        pass
