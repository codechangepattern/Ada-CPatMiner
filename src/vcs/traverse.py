import multiprocessing
import os
import sys
import uuid
import pickle
import time
import json
import subprocess
import datetime

import libadalang as lal

from multiprocessing.pool import Pool
from log import logger
from pathlib import Path
from pydriller import Repository
from pydriller.domain.commit import ModificationType

import settings
import changegraph
from utils.ada_node_id_mapper import AdaNodeIdMapper
from utils.ada_node_visitor import accept


class GitAnalyzer:
    GIT_REPOSITORIES_DIR = settings.get('git_repositories_dir')
    STORAGE_DIR = settings.get('change_graphs_storage_dir')
    STORE_INTERVAL = settings.get('change_graphs_store_interval', 50)
    TRAVERSE_ASYNC = settings.get('traverse_async', True)
    TRAVERSE_MAX_COMMITS = settings.get('traverse_max_commits', 1000)

    MIN_DATE = None
    if settings.get('traverse_min_date', required=False):
        MIN_DATE = datetime.datetime.strptime(settings.get('traverse_min_date', required=False), '%d.%m.%Y') \
            .replace(tzinfo=datetime.timezone.utc)

    def __init__(self):
        self._data_file_dir = os.path.join(self.GIT_REPOSITORIES_DIR, '.data.json')
        self._data = {
            'in_progress': [],  # todo
            'visited': []
        }

        self._load_data_file()

    def _load_data_file(self):
        with open(self._data_file_dir, 'a+') as f:
            f.seek(0)
            data = f.read()

        if data:
            try:
                self._data = json.loads(data)
            except:
                logger.warning('Unable to load existing git repo data file')

    def _save_data_file(self):
        with open(self._data_file_dir, 'w+') as f:
            json.dump(self._data, f, indent=4)

    def build_change_graphs(self):
        repo_names = [
            name for name in os.listdir(self.GIT_REPOSITORIES_DIR)
            if not name.startswith('_') and not name.startswith('.') and name not in self._data['visited']]

        if not repo_names:
            logger.warning('No available repositories were found')
            return

        logger.warning(f'Found {len(repo_names)} repositories, starting a build process')
        self._mine_changes(repo_names)

    def _mine_changes(self, repo_names, pool=None):
        for repo_num, repo_name in enumerate(repo_names):
            logger.warning(f'Looking at repo {repo_name} [{repo_num + 1}/{len(repo_names)}]')

            self._data['visited'].append(repo_name)
            self._save_data_file()

            start = time.time()
            commits = self._extract_commits(repo_name)

            if GitAnalyzer.TRAVERSE_ASYNC:
                with Pool(processes=multiprocessing.cpu_count()) as pool:
                    pool.imap_unordered(self._build_and_store_change_graphs, commits)
                    pool.close()
                    pool.join()
            else:
                for commit in commits:
                    self._build_and_store_change_graphs(commit)

            logger.warning(f'Done building change graphs for repo={repo_name} [{repo_num + 1}/{len(repo_names)}]',
                           start_time=start)

    def _extract_commits(self, repo_name):
        start = time.time()

        repo_path = os.path.join(self.GIT_REPOSITORIES_DIR, repo_name)
        repo_url = self._get_repo_url(repo_path)
        repo = Repository(repo_path, order='reverse', only_no_merge=True)
        commits_traversed = 0

        for commit in repo.traverse_commits():
            logger.warning(f'commits traversed {commits_traversed}')
            if commits_traversed >= GitAnalyzer.TRAVERSE_MAX_COMMITS:
                break
            if not commit.parents:
                continue

            if self.MIN_DATE and commit.committer_date < self.MIN_DATE:
                continue

            cut = {
                'author': {
                    'email': commit.author.email,
                    'name': commit.author.name
                } if commit.author else None,
                'num': commits_traversed + 1,
                'hash': commit.hash,
                'dtm': commit.committer_date,
                'msg': commit.msg,
                'modifications': [],
                'repo': {
                    'name': repo_name,
                    'path': repo_path,
                    'url': repo_url
                }
            }

            for mod in commit.modified_files:
                try:
                    cut['modifications'].append({
                        'type': mod.change_type,

                        'old_src': mod.source_code_before,
                        'old_path': mod.old_path,

                        'new_src': mod.source_code,
                        'new_path': mod.new_path,

                        'repo_name': repo_name
                    })
                except ValueError:
                    logger.warning(f'Could not find commit {mod}')

            yield cut
            commits_traversed += 1

    @staticmethod
    def _get_repo_url(repo_path):
        args = ['git', 'config', '--get', 'remote.origin.url']
        result = subprocess.run(args, stdout=subprocess.PIPE, cwd=repo_path).stdout.decode('utf-8')
        return result.strip()

    @staticmethod
    def _store_change_graph(graph):
        if len(graph.nodes) == 0:
            return
        # if graph.repo_info and graph.repo_info.repo_name:
        #     changegraph.export_graph_image(graph, os.path.join(GitAnalyzer.STORAGE_DIR,
        #                                                        graph.repo_info.repo_name,
        #                                                        f'{str(uuid.uuid4())}.dot'))

        filename = uuid.uuid4().hex
        logger.info(f'Trying to store graph to {filename}', show_pid=True)
        filename = os.path.join(GitAnalyzer.STORAGE_DIR, graph.repo_info.repo_name, f'{filename}.pickle')
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w+b') as f:
            pickle.dump(graph, f, protocol=5)
        logger.info(f'Storing graphs to {filename} finished', show_pid=True)

    @staticmethod
    def _build_and_store_change_graphs(commit):
        commit_msg = commit['msg'].replace('\n', '; ')
        logger.info(f'Looking at commit #{commit["hash"]}, msg: "{commit_msg}"', show_pid=True)

        for mod in commit['modifications']:
            if mod['type'] != ModificationType.MODIFY:
                continue

            if not all([mod['old_path'].endswith('.adb'), mod['new_path'].endswith('.adb')]):
                continue

            old_method_to_new = GitAnalyzer._get_methods_mapping(
                GitAnalyzer._extract_methods(mod['old_path'], mod['old_src'], mod['repo_name']),
                GitAnalyzer._extract_methods(mod['new_path'], mod['new_src'], mod['repo_name'])
            )

            for old_method, new_method in old_method_to_new.items():
                old_method_src = old_method.get_source()
                new_method_src = new_method.get_source()

                if not all([old_method_src, new_method_src]) or old_method_src.strip() == new_method_src.strip():
                    continue

                line_count = max(old_method_src.count('\n'), new_method_src.count('\n'))
                if line_count > settings.get('traverse_file_max_line_count'):
                    logger.info(f'Ignored files due to line limit: {mod["old_path"]} -> {mod["new_src"]}')
                    continue

                repo_info = RepoInfo(
                    commit['repo']['name'],
                    commit['repo']['path'],
                    commit['repo']['url'],
                    commit['hash'],
                    commit['dtm'],
                    mod['old_path'],
                    mod['new_path'],
                    old_method,
                    new_method,
                    author_email=commit['author']['email'] if commit.get('author') else None,
                    author_name=commit['author']['name'] if commit.get('author') else None
                )

                try:
                    cg = changegraph.build_from_trees(old_method.ast, new_method.ast, old_method.src, new_method.src, repo_info=repo_info)
                except:
                    logger.log(logger.ERROR,
                               f'Unable to build a change graph for '
                               f'repo={commit["repo"]["path"]}, '
                               f'commit=#{commit["hash"]}, '
                               f'method={old_method.full_name}, '
                               f'line={old_method.ast.sloc_range}', exc_info=True, show_pid=True)
                    continue

                GitAnalyzer._store_change_graph(cg)

    @staticmethod
    def _extract_methods(file_path, src, repo_name):
        project_path = os.path.join(GitAnalyzer.GIT_REPOSITORIES_DIR, repo_name)

        # if os.path.exists(os.path.join(project_path, GitAnalyzer.GIT_REPOSITORIES[repo_name])):
        #     unit_provider = lal.GPRProject(os.path.join(project_path, GitAnalyzer.GIT_REPOSITORIES[repo_name])).create_unit_provider()
        #     context = lal.AnalysisContext(unit_provider=unit_provider)
        # else:
        context = lal.AnalysisContext()

        unit = context.get_from_buffer(os.path.join(project_path, file_path), src)
        ast = unit.root

        id_mapper = AdaNodeIdMapper()
        accept(ast, id_mapper)

        methods: list[lal.SubpBody] = ast.findall(lambda n: isinstance(n, lal.SubpBody))
        return [Method(file_path, m.f_subp_spec.f_subp_name.text, m, src, id_mapper.node_id[m]) for m in methods if m.f_subp_spec.f_subp_name is not None]

    @staticmethod
    def _set_unique_names(methods):
        method_name_to_cnt = {}
        for method in methods:
            cnt = method_name_to_cnt.setdefault(method.full_name, 0) + 1
            method_name_to_cnt[method.full_name] = cnt

            if cnt > 1:
                method.full_name += f'#{cnt}'

    @staticmethod
    def _get_methods_mapping(old_methods, new_methods):
        GitAnalyzer._set_unique_names(old_methods)
        GitAnalyzer._set_unique_names(new_methods)

        old_method_to_new = {}
        for old_method in old_methods:
            for new_method in new_methods:
                if old_method.full_name == new_method.full_name:
                    old_method_to_new[old_method] = new_method
        return old_method_to_new


class Method:
    def __init__(self, path, name, ast, src, node_id):
        self.file_path = path
        self.ast = ast
        self.ast_node_id = node_id
        self.source = ast.text
        self.src = src

        self.name = name
        self.full_name = name

    def extend_path(self, prefix, separator='.'):
        self.full_name = f'{prefix}{separator}{self.full_name}'

    def get_source(self):
        return self.source

    def __getstate__(self):
        state = self.__dict__.copy()
        if 'ast' in state:
            del state['ast']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

    def get_ast(self):
        if not hasattr(self, 'ast'):
            id_mapper = AdaNodeIdMapper()
            context = lal.AnalysisContext()
            unit = context.get_from_buffer(self.file_path, self.src)
            accept(unit.root, id_mapper)
            self.ast = id_mapper.id_node[self.ast_node_id]
        return self.ast


class RepoInfo:
    def __init__(self, repo_name, repo_path, repo_url, commit_hash, commit_dtm,
                 old_file_path, new_file_path, old_method, new_method,
                 author_email=None, author_name=None):
        self.repo_name = repo_name
        self.repo_path = repo_path
        self.repo_url = repo_url

        self.commit_hash = commit_hash
        self.commit_dtm = commit_dtm

        self.old_file_path = old_file_path
        self.new_file_path = new_file_path

        self.old_method = old_method
        self.new_method = new_method

        self.author_email = author_email
        self.author_name = author_name