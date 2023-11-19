from libadalang import AnalysisContext, AnalysisUnit, AdaNode

from src.treed.treed import TreedMapper


def main():
    context = AnalysisContext()
    unit_a: AnalysisUnit = context.get_from_file('../a.adb')
    unit_b: AnalysisUnit = context.get_from_file('../b.adb')
    node_a: AdaNode = unit_a.root
    node_b: AdaNode = unit_b.root
    treed_mapper: TreedMapper = TreedMapper(node_a, node_b)
    treed_mapper.map(False)
    treed_mapper.print_changes()
    print('Number of changed AST nodes: {}'.format(treed_mapper.get_number_of_changes()))
    print('Number of unmaps: {}'.format(treed_mapper.get_number_of_unmaps()))
    print('Number of non name unmaps: {}'.format(treed_mapper.get_number_of_non_name_unmaps()))


if __name__ == '__main__':
    main()
