from gumtree.tree.tree_metrics import TreeMetrics
from gumtree.tree.tree_visitor import InnerNodesAndLeavesVisitor


class TreeMetricComputer(InnerNodesAndLeavesVisitor):
    ENTER = "enter"
    LEAVE = "leave"
    BASE = 33

    def __init__(self):
        self.current_depth = 0
        self.current_position = 0

    def start_inner_node(self, tree):
        self.current_depth += 1

    def visit_leaf(self, tree):
        tree.set_metrics(TreeMetrics(
            1,
            0,
            self.leaf_hash(tree),
            self.leaf_structure_hash(tree),
            self.current_depth,
            self.current_position
        ))
        self.current_position += 1

    def end_inner_node(self, tree):
        self.current_depth -= 1
        sum_size = 0
        max_height = 0
        current_hash = 0
        current_structure_hash = 0

        for child in tree.get_children():
            metrics = child.get_metrics()
            exponent = 2 * sum_size + 1
            current_hash += metrics.hash * self.hash_factor(exponent)
            current_structure_hash += metrics.structure_hash * self.hash_factor(exponent)
            sum_size += metrics.size
            if metrics.height > max_height:
                max_height = metrics.height

        tree.set_metrics(TreeMetrics(
            sum_size + 1,
            max_height + 1,
            self.inner_node_hash(tree, 2 * sum_size + 1, current_hash),
            self.inner_node_structure_hash(tree, 2 * sum_size + 1, current_structure_hash),
            self.current_depth,
            self.current_position
        ))
        self.current_position += 1

    @staticmethod
    def hash_factor(exponent):
        return TreeMetricComputer.fast_exponentiation(TreeMetricComputer.BASE, exponent)

    @staticmethod
    def fast_exponentiation(base, exponent):
        if exponent == 0:
            return 1
        if exponent == 1:
            return base
        result = 1
        while exponent > 0:
            if exponent & 1:
                result *= base
            exponent >>= 1
            base *= base
        return result

    @staticmethod
    def inner_node_hash(tree, size, middle_hash):
        return hash((tree.get_type(), tree.get_label(), TreeMetricComputer.ENTER)) + \
               middle_hash + \
               hash((tree.get_type(), tree.get_label(), TreeMetricComputer.LEAVE)) * \
               TreeMetricComputer.hash_factor(size)

    @staticmethod
    def inner_node_structure_hash(tree, size, middle_hash):
        return hash((tree.get_type(), TreeMetricComputer.ENTER)) + \
               middle_hash + \
               hash((tree.get_type(), TreeMetricComputer.LEAVE)) * \
               TreeMetricComputer.hash_factor(size)

    @staticmethod
    def leaf_hash(tree):
        return TreeMetricComputer.inner_node_hash(tree, 1, 0)

    @staticmethod
    def leaf_structure_hash(tree):
        return TreeMetricComputer.inner_node_structure_hash(tree, 1, 0)
