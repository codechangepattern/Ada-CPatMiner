class TreeUtils:
    @staticmethod
    def pre_order(tree):
        trees = []
        TreeUtils._pre_order(tree, trees)
        return trees

    @staticmethod
    def _pre_order(tree, trees):
        trees.append(tree)
        if not tree.is_leaf():
            for c in tree.get_children():
                TreeUtils._pre_order(c, trees)

    @staticmethod
    def post_order(tree):
        trees = []
        TreeUtils._post_order(tree, trees)
        return trees

    @staticmethod
    def _post_order(tree, trees):
        if not tree.is_leaf():
            for c in tree.get_children():
                TreeUtils._post_order(c, trees)
        trees.append(tree)

    @staticmethod
    def breadth_first(tree):
        trees = []
        currents = [tree]
        while currents:
            c = currents.pop(0)
            trees.append(c)
            currents.extend(c.get_children())
        return trees

    @staticmethod
    def breadth_first_iterator(tree):
        fifo = [tree]
        for item in fifo:
            yield item
            fifo.extend(item.get_children())

    @staticmethod
    def post_order_iterator(tree):
        stack = [(tree, iter(tree.get_children()))]
        while stack:
            node, children_iter = stack[-1]
            try:
                child = next(children_iter)
                stack.append((child, iter(child.get_children())))
            except StopIteration:
                stack.pop()
                yield node

    @staticmethod
    def pre_order_iterator(tree):
        stack = [iter([tree])]
        while stack:
            children_iter = stack[-1]
            try:
                child = next(children_iter)
                yield child
                if not child.is_leaf():
                    stack.append(iter(child.get_children()))
            except StopIteration:
                stack.pop()

    @staticmethod
    def leaf_iterator(tree_iterator):
        for t in tree_iterator:
            if t.is_leaf():
                yield t
