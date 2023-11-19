from __future__ import annotations

from typing import Set

from gumtree import GumTree
from log import logger

import vb_utils


class Node:
    class Property:
        UNMAPPABLE = 'unmappable'
        SYNTAX_TOKEN_INTERVALS = 'syntax-tokens'

        DEF_FOR = 'def-for'
        DEF_BY = 'def-by'

        DEF_CONTROL_BRANCH_STACK = 'def-stack'
        # ORDER = 'order'  # todo

    def set_property(self, prop, value):
        self._data[prop] = value

    def update_property(self, prop, value):
        self._data[prop] = vb_utils.deep_merge(self._data.get(prop), value)

    def get_property(self, prop, default=None):
        return self._data.get(prop, default)

    class Version:
        BEFORE_CHANGES = 0
        AFTER_CHANGES = 1

    def __init__(self, label, ast, /, *, version=Version.BEFORE_CHANGES):
        global _statement_cnt
        self.statement_num = _statement_cnt
        _statement_cnt += 1

        self.label = str(label)
        self.ast = ast

        self.mapped = None

        self.in_edges = set()  # todo: make protected some fields
        self.out_edges = set()

        self.version = version

        self._data = {}

    def get_definitions(self):
        defs = set()
        for e in self.in_edges:
            if isinstance(e, DataEdge) and e.label == LinkType.REFERENCE:
                defs.add(e.node_from)
        return defs

    def create_edge(self, node_to, link_type):
        e = DataEdge(link_type, node_from=self, node_to=node_to)
        self.out_edges.add(e)
        node_to.in_edges.add(e)

    def has_in_edge(self, node_from, label):
        for e in self.in_edges:
            if e.node_from == node_from and e.label == label:
                return True
        return False

    def remove_in_edge(self, e):
        self.in_edges.remove(e)
        e.node_from.out_edges.remove(e)

    def remove_out_edge(self, e):
        self.out_edges.remove(e)
        e.node_to.in_edges.remove(e)

    def get_incoming_nodes(self, /, *, label=None):
        result = set()
        for e in self.in_edges:
            if not label or e.label == label:
                result.add(e.node_from)
        return result

    def get_outgoing_nodes(self, /, *, label=None):
        result = set()
        for e in self.out_edges:
            if not label or e.label == label:
                result.add(e.node_to)
        return result

    def __repr__(self):
        return f'#{self.statement_num}'


class DataNode(Node):
    class Kind:
        VARIABLE_DECL = 'variable-decl'
        VARIABLE_USAGE = 'variable-usage'
        DUMMY_DECL = 'dummy-decl'
        DUMMY_USAGE = 'dummy-usage'
        PACKAGE_USAGE = 'package-usage'
        SUBSCRIPT = 'subscript'
        SUBTYPE_INDICATION = 'subtype-indication'
        SLICE = 'slice'
        LITERAL = 'literal'
        KEYWORD = 'keyword'
        QUANTIFIER = 'quantifier'
        UNDEFINED = 'undefined'

    def __init__(self, label, ast, /, *, key=None, kind=None):
        super().__init__(label, ast)

        self.key = key
        self.kind = kind or self.Kind.UNDEFINED

    def __repr__(self):
        return f'#{self.statement_num} {self.label} <{self.kind}>'


class StatementNode(Node):
    def __init__(self, label, ast, control_branch_stack, /):
        super().__init__(label, ast)

        self.control_branch_stack = control_branch_stack.copy()

        if not isinstance(self, EntryNode) and control_branch_stack:
            control, branch_kind = control_branch_stack[-1]
            if control:
                control.create_control_edge(self, branch_kind, add_to_stack=False)

    @property
    def control(self):
        control, _ = self.control_branch_stack[-1]
        return control

    @property
    def branch_kind(self):
        _, branch_kind = self.control_branch_stack[-1]
        return branch_kind

    def create_control_edge(self, node_to, branch_kind, /, add_to_stack=True):
        e = ControlEdge(node_from=self, node_to=node_to, branch_kind=branch_kind)
        self.out_edges.add(e)
        node_to.in_edges.add(e)

        if add_to_stack:
            node_to.control_branch_stack.append((self, branch_kind))

    def reset_controls(self):
        for e in list(self.in_edges):
            if isinstance(e, ControlEdge):
                self.remove_in_edge(e)

        self.control_branch_stack = []


class EmptyNode(StatementNode):
    def __init__(self, control_branch_stack, /):
        super().__init__('empty', None, control_branch_stack)  # TODO: None was previously ast.


class OperationNode(StatementNode):
    class Label:
        ALLOCATION = 'new'
        ASSIGN = ':='
        COMPREHENSION = 'comprehension'
        CONTINUE = 'continue'
        DELTA = 'delta'
        DEREFERENCE = 'all'
        DELAY = 'delay'
        DELAYUNTIL = 'delay-until'
        DICTCOMP = 'DictComprehension'
        EXIT = 'exit'
        GENERATOREXPR = 'GeneratorExpression'
        LAMBDA = 'lambda'
        LISTCOMP = 'ListComprehension'
        NULL = 'null'
        QUANTIFIEDEXPR = 'QuantifiedExpr'
        RAISE = 'raise'
        RETURN = 'return'

    class Kind:
        AGGREGATE = 'aggregate'
        ALLOCATION = 'allocation'
        ALTERNATIVES = 'alternatives'
        ASSIGN = 'assignment'
        ASSOCIATION = 'association'
        ATTRIBUTE_REF = 'attr-ref'
        BINARY = 'binary'
        BOOL = 'bool'
        COLLECTION = 'collection'
        COMPARE = 'comparision'
        COMPREHENSION = 'comprehension'
        CONTINUE = 'continue'
        DELAY = 'delay'
        DELAYUNTIL = 'delay-until'
        DEREFERENCE = 'dereference'
        DICTCOMP = 'dict-comp'
        EXIT = 'exit'
        FUNC_CALL = 'func-call'
        QUALIFIEDEXPR = 'qualified-expr'
        QUANTIFIEDEXPR = 'quantified-expr'
        RAISE = 'raise'
        RETURN = 'return'
        UNARY = 'unary'
        UNCLASSIFIED = 'unclassified'

    def __init__(self, label, ast, control_branch_stack, /, *, kind=None, key=None):
        super().__init__(label, ast, control_branch_stack)
        self.kind = kind or self.Kind.UNCLASSIFIED
        self.key = key

    def __repr__(self):
        return f'#{self.statement_num} {self.label} <{self.kind}>'


class ControlNode(StatementNode):
    class Label:
        IF = 'if'
        FOR = 'for'
        WHILE = 'while'
        LOOP = 'loop'
        TRY = 'try'
        EXCEPT = 'except'
        ASSERT = 'assert'

        ALL = [IF, FOR, TRY, EXCEPT, ASSERT]

    def __init__(self, label, ast, control_branch_stack, /):
        super().__init__(label, ast, control_branch_stack)

    def __repr__(self):
        return f'#{self.statement_num} {self.label}'


class EntryNode(ControlNode):
    def __init__(self, ast, /):
        super().__init__('START', ast, [])


class Edge:
    def __init__(self, label, node_from, node_to):
        self.label = label
        self.node_from = node_from
        self.node_to = node_to

    def __repr__(self):
        return f'{self.node_from} ={self.label}> {self.node_to}'


class ControlEdge(Edge):
    def __init__(self, /, *, node_from, node_to, branch_kind=True):
        super().__init__('control', node_from, node_to)
        self.branch_kind = branch_kind

    def __repr__(self):
        return f'{self.node_from} ={self.label}> {self.node_to} [{self.branch_kind}]'


class DataEdge(Edge):
    def __init__(self, label, node_from, node_to):  # FIXME: DO NO CONSIDER LABEL AS LINK_TYPE, DEFINE A NEW INDICATOR
        super().__init__(label, node_from, node_to)


class LinkType:
    DEFINITION = 'def'
    RECEIVER = 'recv'
    REFERENCE = 'ref'
    PARAMETER = 'para'
    CONDITION = 'cond'
    QUALIFIER = 'qual'

    # special
    MAP = 'map'
    CONTROL = 'control'

    # hidden link types
    DEPENDENCE = 'dep'


class ExtControlFlowGraph:
    def __init__(self, visitor, /, *, node=None):
        self.visitor = visitor

        self.entry_node = None
        self.nodes: Set[Node] = set()
        self.op_nodes: Set[OperationNode] = set()

        self.var_refs = set()

        self.sinks: Set[Node] = set()
        self.statement_sinks: Set[StatementNode] = set()
        self.statement_sources: Set[StatementNode] = set()

        if node:
            self.nodes.add(node)
            self.sinks.add(node)

            if isinstance(node, StatementNode):
                self.statement_sinks.add(node)
                self.statement_sources.add(node)

            if isinstance(node, OperationNode):
                self.op_nodes.add(node)

        self.changed_nodes = set()

    def _resolve_refs(self, graph):
        resolved_refs = set()
        for ref_node in graph.var_refs:
            def_nodes = self.visitor.context.get_variables(ref_node.key)
            if def_nodes:
                for def_node in def_nodes:
                    if def_node.statement_num < ref_node.statement_num:
                        def_node.create_edge(ref_node, LinkType.REFERENCE)
                resolved_refs.add(ref_node)
        return resolved_refs

    def merge_graph(self, graph, /, *, link_node=None, link_type=None):
        if link_node and link_type:
            for sink in self.sinks:
                sink.create_edge(link_node, link_type)

        self.nodes = self.nodes.union(graph.nodes)
        self.op_nodes = self.op_nodes.union(graph.op_nodes)

        resolved_refs = self._resolve_refs(graph)
        unresolved_refs = graph.var_refs.difference(resolved_refs)

        for sink in self.statement_sinks:
            for source in graph.statement_sources:
                sink.create_edge(source, link_type=LinkType.DEPENDENCE)

        self.sinks = graph.sinks
        self.statement_sinks = graph.statement_sinks

        self.var_refs = self.var_refs.union(unresolved_refs)

    def parallel_merge_graphs(self, graphs, op_link_type=None):
        old_sinks = self.sinks.copy()
        old_statement_sinks = self.statement_sinks.copy()

        self.sinks.clear()
        self.statement_sinks.clear()

        for graph in graphs:
            resolved_refs = self._resolve_refs(graph)
            unresolved_refs = graph.var_refs.difference(resolved_refs)

            if op_link_type:
                for op_node in graph.op_nodes:
                    for sink in old_sinks:
                        if not op_node.has_in_edge(sink, op_link_type):
                            sink.create_edge(op_node, op_link_type)

            for sink in old_statement_sinks:
                for source in graph.statement_sources:
                    sink.create_edge(source, link_type=LinkType.DEPENDENCE)

            self.nodes = self.nodes.union(graph.nodes)
            self.op_nodes = self.op_nodes.union(graph.op_nodes)
            self.sinks = self.sinks.union(graph.sinks)
            self.var_refs = self.var_refs.union(unresolved_refs)

            self.statement_sinks = self.statement_sinks.union(graph.statement_sinks)
            # self.statement_sources = self.statement_sources.union(graph.statement_sources)

    def add_node(self, node: Node, /, *, link_type=None, clear_sinks=False):
        if link_type:
            for sink in self.sinks:
                sink.create_edge(node, link_type)

        if getattr(node, 'key', None):
            if link_type != LinkType.DEFINITION:
                self.var_refs.add(node)

        if clear_sinks:
            self.sinks.clear()

        self.sinks.add(node)
        self.nodes.add(node)

        if isinstance(node, StatementNode):
            for sink in self.statement_sinks:
                sink.create_edge(node, link_type=LinkType.DEPENDENCE)

            self.statement_sinks.clear()
            self.statement_sinks.add(node)

            if not self.statement_sources:
                self.statement_sources.add(node)

        if isinstance(node, OperationNode):
            self.op_nodes.add(node)

    def remove_node(self, node):
        for e in node.in_edges:
            e.node_from.out_edges.remove(e)

        for e in node.out_edges:
            e.node_to.in_edges.remove(e)

        node.in_edges.clear()
        node.out_edges.clear()

        self.nodes.remove(node)
        self.op_nodes.discard(node)

        self.sinks.discard(node)
        self.statement_sinks.discard(node)

    def set_entry_node(self, entry_node):
        if self.entry_node:
            raise EntryNodeDuplicated

        self.entry_node = entry_node
        self.nodes.add(entry_node)

    def get_control_nodes(self):
        control_nodes = []
        for node in self.nodes:
            if isinstance(node, ControlNode):
                control_nodes.append(node)

    @staticmethod
    def map_by_gumtree(fg1, fg2, gumtree: GumTree):
        ast_mapping = {}
        for mapping in gumtree.mappings:
            ast_mapping[mapping.first.ast] = mapping.second.ast

        fg_dest_node_map = {}
        for fg_dest_node in fg2.nodes:
            if fg_dest_node.ast:
                fg_dest_node_map[fg_dest_node.ast] = fg_dest_node
        for fg_src_node in fg1.nodes:
            if fg_src_node.ast:
                if fg_src_node.ast in ast_mapping:
                    mapped_ast = ast_mapping[fg_src_node.ast]
                    fg_dest_node = fg_dest_node_map.get(mapped_ast)
                    if fg_dest_node:
                        fg_src_node.mapped = fg_dest_node
                        fg_dest_node.mapped = fg_src_node
                        fg_src_node.create_edge(fg_dest_node, LinkType.MAP)

    @staticmethod
    def absolute_position_by_gumtree(fg1, fg2, gumtree: GumTree):
        for node in fg1.nodes:
            gumtree_node = gumtree.diff.src.trees[node.ast]
            node.start_pos = gumtree_node.pos - gumtree.diff.src.trees[fg1.entry_node.ast].pos
            node.end_pos = node.start_pos + gumtree_node.length
        for node in fg2.nodes:
            gumtree_node = gumtree.diff.dst.trees[node.ast]
            node.start_pos = gumtree_node.pos - gumtree.diff.dst.trees[fg2.entry_node.ast].pos
            node.end_pos = node.start_pos + gumtree_node.length

    def _get_transitive_change_nodes(self, gumtree):
        result = set()
        for node in self.changed_nodes:
            refs = node.get_outgoing_nodes(label=LinkType.REFERENCE)
            for ref in refs:
                out_nodes = ref.get_outgoing_nodes()
                for out_node in out_nodes:
                    if out_node in self.changed_nodes and gumtree.is_node_changed(node.ast):
                        result.add(ref)
                        break
        return result

    @staticmethod
    def _get_node_dependencies(node):
        result = node.get_definitions()
        return result

    def calc_changed_nodes_by_gumtree(self, gumtree):
        self.changed_nodes.clear()

        for node in self.nodes:
            if isinstance(node, EntryNode):
                continue

            if node.get_property(Node.Property.UNMAPPABLE):
                continue

            if gumtree.is_node_changed(node.ast):
                self.changed_nodes.add(node)

                deps = self._get_node_dependencies(node)
                self.changed_nodes = self.changed_nodes.union(deps)

        self.changed_nodes = self.changed_nodes.union(self._get_transitive_change_nodes(gumtree))

    def find_node_by_label(self, label):
        for node in self.nodes:
            if node.label == label:
                return node
        return None


_statement_cnt = 0


class EntryNodeDuplicated(Exception):  # TODO: move outside of this file
    pass


class TreedMappingException(Exception):
    pass
