from libadalang import AnalysisContext, AnalysisUnit, AdaNode

from gumtree import GumTree
from treed.treed import TreedMapper


def test_tree_mapping():
    prefix = 'examples/double_negation'
    for i in range(0, 1):
        path_old = f'{prefix}/{i}_old.adb'
        path_new = f'{prefix}/{i}_new.adb'
        with open(path_old, 'r') as src1, open(path_new, 'r') as src2:
            context = AnalysisContext()
            unit_old = context.get_from_file(path_old)
            unit_new = context.get_from_file(path_new)
            node_old = unit_old.root
            node_new = unit_new.root
            gumtree = GumTree(node_old, src1.read(), node_new, src2.read())
            print('Number of deletions: {}'.format(gumtree.deletions))


if __name__ == '__main__':
    test_tree_mapping()