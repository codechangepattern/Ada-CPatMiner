import changegraph


def test_change_graphs():
    prefix = 'examples/double_negation'
    for i in range(0, 3):
        cg = changegraph.build_from_files(f'{prefix}/{i}_old.adb', f'{prefix}/{i}_new.adb')
        changegraph.export_graph_image(cg, f'double_negation/test_{i}')


if __name__ == '__main__':
    test_change_graphs()