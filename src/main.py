import os
import argparse
import multiprocessing
import pickle
import sys

import adaflowgraph
import changegraph
from log import logger
from vcs.traverse import GitAnalyzer
from patterns import Miner
import settings

class RunModes:
    BUILD_ADA_FLOW_GRAPH = 'afg'
    BUILD_CHANGE_GRAPH = 'cg'
    COLLECT_CHANGE_GRAPHS = 'collect-cgs'
    CHANGE_GRAPHS_INFO = 'cgs-info'
    MINE_PATTERNS = 'patterns'
    ALL = [BUILD_ADA_FLOW_GRAPH, BUILD_CHANGE_GRAPH, COLLECT_CHANGE_GRAPHS, MINE_PATTERNS]


def main():
    logger.info('------------------------------ Starting ------------------------------')

    multiprocessing.set_start_method('spawn', force=True)

    parser = argparse.ArgumentParser()
    parser.add_argument('mode', help=f'One of {RunModes.ALL}', type=str)
    args, _ = parser.parse_known_args()

    current_mode = args.mode
    # for example: afg -i c.adb
    if current_mode == RunModes.BUILD_ADA_FLOW_GRAPH:
        parser.add_argument('-i', '--input', help='Path to source code file', type=str, required=True)
        parser.add_argument('-o', '--output', help='Path to output file', type=str, default='adaflowgraph.dot')
        parser.add_argument('--no-closure', action='store_true')
        parser.add_argument('--show-deps', action='store_true')
        parser.add_argument('--hide-op-kinds', action='store_true')
        parser.add_argument('--show-data-keys', action='store_true')
        args = parser.parse_args()

        flow_graph = adaflowgraph.build_from_file(
            args.input, show_dependencies=args.show_deps, build_closure=not args.no_closure
        )
        adaflowgraph.export_graph_image(
            flow_graph, args.output, show_op_kinds=not args.hide_op_kinds, show_data_keys=args.show_data_keys
        )
    # for example: cg -s a.adb -d b.adb
    elif current_mode == RunModes.BUILD_CHANGE_GRAPH:
        parser.add_argument('-s', '--src', help='Path to source code before changes', type=str, required=True)
        parser.add_argument('-d', '--dest', help='Path to source code after changes', type=str, required=True)
        parser.add_argument('-o', '--output', help='Path to output file', type=str, default='changegraph.dot')
        args = parser.parse_args()

        fg = changegraph.build_from_files(args.src, args.dest)
        changegraph.export_graph_image(fg, args.output)
        GitAnalyzer._store_change_graphs([fg])
    elif current_mode == RunModes.COLLECT_CHANGE_GRAPHS:
        GitAnalyzer().build_change_graphs()
    elif current_mode == RunModes.MINE_PATTERNS:
        logger.warning('Pattern mining has started.')

        miner = Miner()
        try:
            miner.mine_patterns(change_graphs_from_disk())
        except KeyboardInterrupt:
            logger.warning('KeyboardInterrupt: mined patterns will be stored before exit.')
        
        miner.print_patterns()
    elif current_mode == 'test':
        sizes = []
        for graph in change_graphs_from_disk():
            sizes.append(len(graph.nodes))

        print(min(sizes))
        print(max(sizes))
        print(len([size for size in sizes if size > 150]))
    elif current_mode == RunModes.CHANGE_GRAPHS_INFO:
        change_graphs_info(change_graphs_from_disk())


def change_graphs_from_disk():
    storage_dir = settings.get('change_graphs_storage_dir')
    dir_names = os.listdir(storage_dir)

    for dir_num, dir_name in enumerate(dir_names):
        dir_path = os.path.join(storage_dir, dir_name)
        file_names = os.listdir(dir_path)
        logger.warning(f'Loading project [{1 + dir_num}/{len(dir_names)}].')
        for file_num, file_name in enumerate(file_names):
            file_path = os.path.join(dir_path, file_name)
            try:
                with open(file_path, 'rb') as f:
                    graph = pickle.load(f)

                    if len(graph.nodes) > 100:
                        logger.warning(f'Skipping graph with size {len(graph.nodes)}.')
                        continue
                    yield graph
            except:
                logger.warning(f'Incorrect file {file_path}.')


def change_graphs_info(graphs):
    graph_dict = {}
    commit_dict = {}
    for graph in graphs:
        graph_set = graph_dict.setdefault(graph.repo_info.repo_name, set())
        graph_set.add(graph)
        commit_set = commit_dict.setdefault(graph.repo_info.repo_name, set())
        commit_set.add(graph.repo_info.commit_hash)
    for repo in graph_dict:
        print(f'Repository {repo} extracted {len(graph_dict[repo])} change graphs, from {len(commit_dict[repo])} commits.')


if __name__ == '__main__':
    main()