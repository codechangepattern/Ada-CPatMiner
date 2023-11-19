class TreeMetrics:
    def __init__(self, size: int, height: int, hash_: int, structure_hash: int, depth: int, position: int):
        """
        Class containing several metrics information regarding a node of an AST.
        The metrics are immutables but lazily computed.

        :param size: The number of nodes in the subtree rooted at the node.
        :param height: The size of the longer branch in the subtree rooted at the node.
        :param hash_: The hashcode of the subtree rooted at the node.
        :param structure_hash: The hashcode of the subtree rooted at the node, excluding labels.
        :param depth: The number of ancestors of a node.
        :param position: An absolute position for the node. Usually computed via the postfix order.
        """
        self.size = size
        self.height = height
        self.hash = hash_
        self.structure_hash = structure_hash
        self.depth = depth
        self.position = position
