import html
import logging
import traceback

import libadalang as lal

import settings
from log import logger
from adaflowgraph.models import Node, DataNode, OperationNode, ExtControlFlowGraph, ControlNode, DataEdge, LinkType, \
    EntryNode, EmptyNode, ControlEdge, StatementNode
from .ast_utils import get_node_key, get_node_short_name, get_node_full_name


class NodeVisitor(object):
    def visit(self, node):
        """Visit a node."""
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise NotImplementedError(node)


class BuildingContext:
    def __init__(self):
        self.var_key_to_def_nodes: dict[set] = {}

    def get_fork(self):
        result = BuildingContext()
        for k, v in self.var_key_to_def_nodes.items():
            result.var_key_to_def_nodes[k] = set().union(v)
        return result

    def add_variable(self, node):
        def_nodes = self.var_key_to_def_nodes.setdefault(node.key, set())
        for def_node in [def_node for def_node in def_nodes if def_node.key == node.key]:
            def_node_stack = def_node.get_property(Node.Property.DEF_CONTROL_BRANCH_STACK)
            node_stack = node.get_property(Node.Property.DEF_CONTROL_BRANCH_STACK)

            if len(def_node_stack) < len(node_stack):
                continue

            if def_node_stack[:len(node_stack)] == node_stack:
                def_nodes.remove(def_node)
        def_nodes.add(node)
        self.var_key_to_def_nodes[node.key] = def_nodes

    def remove_variables(self, control_stack_branch):
        for def_nodes in self.var_key_to_def_nodes.values():
            same_stack_defs = [node for node in def_nodes
                               if node.get_property(Node.Property.DEF_CONTROL_BRANCH_STACK) == control_stack_branch]
            for def_node in same_stack_defs:
                def_nodes.remove(def_node)

    def get_variables(self, var_key):
        return self.var_key_to_def_nodes.get(var_key)


class GraphBuilder:
    def build_from_source(self, file_path, source_code, show_dependencies=False, build_closure=True):
        context = lal.AnalysisContext()
        unit = context.get_from_buffer(file_path, source_code)

        root_node = unit.root

        function_node = root_node.find(lambda n: isinstance(n, lal.SubpBody))

        return self.build_from_tree(function_node, show_dependencies=show_dependencies, build_closure=build_closure)

    def build_from_file(self, file_path, show_dependencies=False, build_closure=True):
        with open(file_path, 'r') as f:
            data = f.read()
        return self.build_from_source(file_path, data, show_dependencies=show_dependencies, build_closure=build_closure)

    def build_from_tree(self, node, show_dependencies=False, build_closure=True):
        log_level = settings.get('logger_file_log_level', 'INFO')

        if log_level != 'DEBUG':
            ada_node_visitor = AdaNodeVisitor()
        else:
            ada_node_visitor = AdaNodeVisitor()

        graph = ada_node_visitor.visit(node)

        if not show_dependencies:
            self.resolve_dependencies(graph)

        if build_closure:
            self.build_closure(graph)

        return graph

    @classmethod
    def _build_data_closure(cls, node, processed_nodes):
        if node.get_definitions():
            return

        for edge in node.in_edges.copy():
            if not isinstance(edge, DataEdge):
                continue

            in_nodes = edge.node_from.get_definitions()
            if not in_nodes:
                in_nodes.add(edge.node_from)
            else:
                for in_node in in_nodes:
                    if not node.has_in_edge(in_node, edge.label):
                        in_node.create_edge(node, edge.label)

            for in_node in in_nodes:
                if in_node not in processed_nodes:
                    cls._build_data_closure(in_node, processed_nodes)

                for in_node_edge in in_node.in_edges:
                    if isinstance(in_node_edge, DataEdge) and not isinstance(in_node_edge.node_from, DataNode):
                        if not in_node_edge.node_from.has_in_edge(node, edge.label):
                            after_in_node = in_node_edge.node_from
                            after_in_node.update_property(
                                Node.Property.DEF_FOR, in_node.get_property(Node.Property.DEF_FOR, []))
                            def_for = after_in_node.get_property(Node.Property.DEF_FOR, [])

                            if edge.label == LinkType.DEFINITION:
                                if not def_for or node.statement_num not in def_for:
                                    continue

                            if not node.has_in_edge(after_in_node, edge.label):
                                after_in_node.create_edge(node, edge.label)

        processed_nodes.add(node)

    @classmethod
    def _build_control_closure(cls, node, processed_nodes):
        if not isinstance(node, ControlNode):
            return

        for in_control in node.get_incoming_nodes(label=LinkType.CONTROL):  # only controls have out control edges now
            if in_control not in processed_nodes:
                cls._build_control_closure(in_control, processed_nodes)

            for e in in_control.in_edges:
                in_control2 = e.node_from
                if not isinstance(e, ControlEdge):
                    continue

                in_control2.create_control_edge(node, e.branch_kind)

        processed_nodes.add(node)

    @classmethod
    def _build_control_data_closure(cls, node, processed_nodes):
        if not isinstance(node, StatementNode):
            return

        logger.debug(f'In node {node}')
        node_controls = {control for (control, branch_kind) in node.control_branch_stack}
        for e in node.in_edges.copy():
            in_node = e.node_from
            if not isinstance(e, ControlEdge) or not isinstance(in_node, ControlNode):  # op nodes processed as in_node2
                continue

            if in_node not in processed_nodes:
                logger.debug(f'Node {in_node} was not visited, going into')
                cls._build_control_data_closure(in_node, processed_nodes)

            visited = set()
            for e2 in in_node.in_edges.copy():
                in_node2 = e2.node_from
                if not isinstance(in_node2, OperationNode) and not isinstance(in_node2, ControlNode):
                    continue
                if in_node2 in visited:
                    continue

                if isinstance(in_node2, ControlNode):
                    if isinstance(node, ControlNode):
                        continue  # the closure is already built

                    lowest_control = in_node2
                else:
                    lowest_control = None  # will be found because the middle node = ControlNode
                    for control in in_node2.get_outgoing_nodes():
                        if not isinstance(control, ControlNode) or control not in node_controls:
                            continue

                        if lowest_control is None or control.statement_num < lowest_control.statement_num:
                            lowest_control = control

                if lowest_control == in_node:
                    branch_kind = e.branch_kind
                else:
                    in_lowest_e = None  # will be found because of control closure made earlier
                    for e3 in lowest_control.out_edges:
                        if e3.label == LinkType.CONTROL and e3.node_to == in_node:
                            in_lowest_e = e3
                            break
                    branch_kind = in_lowest_e.branch_kind

                in_node2.create_control_edge(node, branch_kind, add_to_stack=False)
                logger.debug(f'Created control edge from {in_node2} to {node} with kind = {branch_kind} '
                             f'for node={node}, in_node={in_node}, in_node2={in_node2}')
                visited.add(in_node2)

        processed_nodes.add(node)

    @classmethod
    def _process_fg_nodes(cls, fg, processor_fn):
        logger.debug('-- Starting fg nodes processing --')
        processed_nodes = set()
        for node in fg.nodes:
            if node not in processed_nodes:
                logger.debug(f'Running processor_fn for node {node}')
                processor_fn(node, processed_nodes)

    @classmethod
    def build_closure(cls, fg):
        cls._process_fg_nodes(fg, processor_fn=cls._build_data_closure)
        cls._process_fg_nodes(fg, processor_fn=cls._build_control_closure)
        cls._process_fg_nodes(fg, processor_fn=cls._build_control_data_closure)

    @classmethod
    def _adjust_controls(cls, node, processed_nodes):
        if not isinstance(node, StatementNode):
            return

        in_deps = node.get_incoming_nodes(label=LinkType.DEPENDENCE)
        if not in_deps:
            processed_nodes.add(node)
            return

        control_branch_stacks = []
        control_to_kinds = {}
        for in_dep in in_deps:
            if isinstance(in_dep, ControlNode):
                processed_nodes.add(node)
                return

            if in_dep not in processed_nodes:
                cls._adjust_controls(in_dep, processed_nodes)

            control_branch_stacks.append(in_dep.control_branch_stack)
        control_branch_stacks.append(node.control_branch_stack)

        for stack in control_branch_stacks:
            for control, branch_kind in stack:
                s = control_to_kinds.setdefault(control, set())
                s.add(branch_kind)

        deepest_control = None
        branch_kind = None
        for control, kinds in control_to_kinds.items():
            if len(kinds) == 1:
                if deepest_control is None or deepest_control.statement_num < control.statement_num:
                    deepest_control = control
                    branch_kind = next(iter(kinds))

        if deepest_control:
            node.reset_controls()
            node.control_branch_stack = deepest_control.control_branch_stack.copy()
            deepest_control.create_control_edge(node, branch_kind)
        processed_nodes.add(node)

    @staticmethod
    def _remove_empty_nodes(fg):
        for node in fg.nodes.copy():
            if isinstance(node, EmptyNode):
                fg.remove_node(node)

    @staticmethod
    def _cleanup_deps(fg):
        for node in fg.nodes:
            dep_edges = [e for e in node.in_edges if e.label == LinkType.DEPENDENCE]
            for e in dep_edges:
                node.remove_in_edge(e)

    @classmethod
    def resolve_dependencies(cls, fg):
        cls._process_fg_nodes(fg, processor_fn=cls._adjust_controls)
        cls._remove_empty_nodes(fg)
        cls._cleanup_deps(fg)


class AdaNodeVisitorHelper:
    def __init__(self, ada_node_visitor):
        self.visitor = ada_node_visitor

    def create_graph(self):
        return self.visitor.create_graph()

    def get_type_expr_label(self, node: lal.SubtypeIndication):
        if node.f_constraint:
            return f'{node.text}(*)'
        else:
            return node.text

    def get_exas_label(self, node: lal.Name):
        if isinstance(node, lal.Identifier):
            try:
                if node.p_first_corresponding_decl:
                    if node.p_first_corresponding_decl.f_type_expr:
                        return self.get_type_expr_label(node.p_first_corresponding_decl.f_type_expr)
                return node.text
            except Exception as e:
                print('an exception occurred:', e)
                traceback.print_exc()
                return node.text
        elif isinstance(node, lal.DottedName):
            prefix_label = self.get_exas_label(node.f_prefix)
            suffix_label = node.f_suffix.text
            return f'{prefix_label}.{suffix_label}'
        elif isinstance(node, lal.CallExpr):
            try:
                if isinstance(node.f_name, lal.AttributeRef):
                    return node.f_name.text
                if node.f_name.p_first_corresponding_decl:
                    if node.f_name.p_first_corresponding_decl.f_type_expr:
                        return self.get_type_expr_label(node.f_name.p_first_corresponding_decl.f_type_expr)
                return node.f_name.text
            except Exception as e:
                print('an exception occurred:', e)
                traceback.print_exc()
                return node.f_name.text
        elif isinstance(node, lal.ExplicitDeref):
            return f'{self.get_exas_label(node.f_prefix)}.all'
        else:
            raise NotImplementedError('get_exas_label not implemented')

    def get_assign_graph_and_vars(self, op_node, target, prepared_value):
        if isinstance(target, lal.Name):
            var_name = get_node_full_name(target)
            var_key = get_node_key(target)

            value_graph = prepared_value
            var_node = DataNode(self.get_exas_label(target), target, key=var_key, kind=DataNode.Kind.VARIABLE_DECL)

            sink_nums = []
            for sink in value_graph.sinks:
                sink.update_property(Node.Property.DEF_FOR, [var_node.statement_num])
                sink_nums.append(sink.statement_num)
            var_node.set_property(Node.Property.DEF_BY, sink_nums)

            value_graph.add_node(op_node, link_type=LinkType.PARAMETER)
            value_graph.add_node(var_node, link_type=LinkType.DEFINITION)

            var_node.set_property(Node.Property.DEF_CONTROL_BRANCH_STACK, op_node.control_branch_stack)

            return value_graph, [var_node]
        raise NotImplementedError(target)

    def visit_assign(self, node, targets):
        graph = self.create_graph()
        operation_node = OperationNode(OperationNode.Label.ASSIGN, node, self.visitor.control_branch_stack,
                                       kind=OperationNode.Kind.ASSIGN)

        graphs = []
        assigned_nodes = []
        for target in targets:
            prepared_value = self.visitor.visit(node.f_expr)
            assign_graph, nodes = self.get_assign_graph_and_vars(operation_node, target, prepared_value)
            assigned_nodes += nodes
            graphs.append(assign_graph)

        graph.parallel_merge_graphs(graphs)

        for n in assigned_nodes:
            self.visitor.context.add_variable(n)

        return graph


class AdaNodeVisitor(NodeVisitor):
    def __init__(self):
        self.context_stack = [BuildingContext()]
        self.fg = self.create_graph()

        self.current_control = None
        self.current_branch_kind = True
        self.control_branch_stack = []

        self.visitor_helper = AdaNodeVisitorHelper(self)

        self.log_level = settings.get('logger_file_log_level', 'INFO')

    @property
    def context(self):
        return self.context_stack[-1]

    def create_graph(self, node=None):
        return ExtControlFlowGraph(self, node=node)

    def _switch_context(self, new_context):
        self.context_stack.append(new_context)

    def _pop_context(self):
        self.context_stack.pop()

    def _switch_control_branch(self, new_control, new_branch_kind, replace=False):
        if replace:
            self._pop_control_branch()

        self.control_branch_stack.append((new_control, new_branch_kind))

    def _pop_control_branch(self):
        self.curr_control, self.curr_branch_kind = self.control_branch_stack.pop()

    def _visit_entry_node(self, node: lal.AdaNode):
        # for now an entry node is just always a subprogram body.
        entry_node = EntryNode(node)
        self.fg.set_entry_node(entry_node)
        self._switch_control_branch(entry_node, True)

        param_fgs = []
        if isinstance(node, lal.SubpBody):
            param_fgs = self.visit(node.f_subp_spec)
        self.fg.parallel_merge_graphs(param_fgs)

        if node.f_decls:
            self.fg.merge_graph(self.visit(node.f_decls))

        if node.f_stmts:
            self.fg.merge_graph(self.visit(node.f_stmts))

        self._pop_control_branch()
        return self.fg

    def visit_AdaNodeList(self, nodes: lal.AdaNodeList):
        graph = self.create_graph()
        for node in nodes:
            graph.merge_graph(self.visit(node))
        return graph

    def visit_Aggregate(self, node: lal.Aggregate):
        graph = self.create_graph()

        if node.f_ancestor_expr:
            raise NotImplementedError(node.f_ancestor_expr)

        graph.parallel_merge_graphs([self.visit(assoc) for assoc in node.f_assocs])

        op_node = OperationNode(node.__class__.__name__, node, self.control_branch_stack,
                                kind=OperationNode.Kind.AGGREGATE)
        graph.add_node(op_node, link_type=LinkType.PARAMETER)
        return graph

    def visit_AggregateAssoc(self, node: lal.AggregateAssoc):
        if not len(node.f_designators):
            return self.visit(node.f_r_expr)

        return self._visit_binop(node, node.f_designators, node.f_r_expr,
                                 op_name='=>',
                                 op_kind=OperationNode.Kind.ASSOCIATION)

    def visit_Allocator(self, node: lal.Allocator):
        if node.f_subpool:
            raise NotImplementedError(node)
        return self._visit_op(OperationNode.Label.ALLOCATION, node, OperationNode.Kind.ALLOCATION, [node.f_type_or_expr])

    def visit_AlternativesList(self, node: lal.AlternativesList):
        if len(node) == 1:
            return self.visit(node[0])

        return self._visit_op('|', node, OperationNode.Kind.ALTERNATIVES, node)

    def visit_AssignStmt(self, node: lal.AssignStmt):
        if not isinstance(node.f_dest, lal.Name):
            raise NotImplementedError(node)
        return self.visitor_helper.visit_assign(node, [node.f_dest])

    def visit_AssocList(self, nodes: lal.AssocList):
        graph = self.create_graph()
        associations = []
        for association in nodes:
            associations.append(self.visit(association))
        graph.parallel_merge_graphs(associations)
        return graph

    def visit_AttributeRef(self, node: lal.AttributeRef):
        args_graph = self.visit(node.f_args)

        name = get_node_short_name(node)
        key = get_node_key(node)

        op_node = OperationNode(name, node, self.control_branch_stack, kind=OperationNode.Kind.ATTRIBUTE_REF, key=key)
        args_graph.add_node(op_node, link_type=LinkType.PARAMETER, clear_sinks=True)

        graph = self.visit(node.f_prefix)
        graph.merge_graph(args_graph, link_node=next(iter(args_graph.sinks)), link_type=LinkType.RECEIVER)

        return graph

    def visit_BeginBlock(self, node: lal.BeginBlock):
        return self.visit(node.f_stmts)

    def visit_BinOp(self, node: lal.BinOp):
        return self._visit_binop(node, node.f_left, node.f_right,
                                 op_name=node.f_op.__class__.__name__.lower()[2:],
                                 op_kind=OperationNode.Kind.BINARY)

    def visit_BoxExpr(self, node: lal.BoxExpr):
        return self.create_graph(node=DataNode(self._clear_literal_label(node.text), node, kind=DataNode.Kind.LITERAL))

    def visit_BracketAggregate(self, node: lal.BracketAggregate):
        graph = self.create_graph()

        if node.f_ancestor_expr:
            raise NotImplementedError(node.f_ancestor_expr)

        graph.parallel_merge_graphs([self.visit(assoc) for assoc in node.f_assocs])

        op_node = OperationNode(node.__class__.__name__, node, self.control_branch_stack,
                                kind=OperationNode.Kind.AGGREGATE)
        graph.add_node(op_node, link_type=LinkType.PARAMETER)
        return graph

    def visit_BracketDeltaAggregate(self, node: lal.BracketDeltaAggregate):
        return self._visit_binop(node, node.f_ancestor_expr, node.f_assocs, op_name=OperationNode.Label.DELTA,
                                 op_kind=OperationNode.Kind.AGGREGATE)

    def visit_CallExpr(self, node: lal.CallExpr):
        graph = self.visit(node.f_suffix)

        name = get_node_short_name(node)
        key = get_node_key(node)

        op_node = OperationNode(name, node, self.control_branch_stack, kind=OperationNode.Kind.FUNC_CALL, key=key)

        graph.add_node(op_node, link_type=LinkType.PARAMETER, clear_sinks=True)

        if isinstance(node.f_name, lal.DottedName):
            name: lal.DottedName = node.f_name
            dotted_graph = self.visit(name.f_prefix)
            dotted_graph.merge_graph(graph, link_node=next(iter(graph.sinks)), link_type=LinkType.RECEIVER)
            return dotted_graph
        return graph

    def visit_CallStmt(self, node: lal.CallStmt):
        return self.visit(node.f_call)

    def visit_CaseExpr(self, node: lal.CaseExpr):
        raise NotImplementedError(node)

    def visit_CaseStmt(self, node: lal.CaseStmt):
        raise NotImplementedError(node)

    def visit_CharLiteral(self, node: lal.CharLiteral):
        return self.create_graph(node=DataNode('Char', node, kind=DataNode.Kind.LITERAL))

    def visit_ConcatOp(self, node: lal.ConcatOp):
        operands = iter(node.f_other_operands)
        operand: lal.ConcatOperand = next(operands)
        graph = self._visit_binop(operand, node.f_first_operand, operand.f_operand,
                                  op_name=operand.f_operator.__class__.__name__.lower()[2:],
                                  op_kind=OperationNode.Kind.BINARY)
        for operand in operands:
            left_graph = graph
            op_node = OperationNode(operand.f_operator.__class__.__name__.lower()[2:], operand,
                                    self.control_branch_stack, kind=OperationNode.Kind.BINARY)
            left_graph.add_node(op_node, link_type=LinkType.PARAMETER)
            right_graph = self.visit(operand.f_operand)
            right_graph.add_node(op_node, link_type=LinkType.PARAMETER)
            graph = self.create_graph()
            graph.parallel_merge_graphs([left_graph, right_graph])
        return graph

    def visit_ConcreteTypeDecl(self, node: lal.ConcreteTypeDecl):
        raise NotImplementedError(node)

    def visit_DeclarativePart(self, node: lal.DeclarativePart):
        return self.visit(node.f_decls)

    def visit_DeclBlock(self, node: lal.DeclBlock):
        self._switch_context(self.context.get_fork())
        graph = self.visit(node.f_decls)
        graph.merge_graph(self.visit(node.f_stmts))
        self._pop_context()
        return graph

    def visit_DeclExpr(self, node: lal.DeclExpr):
        raise NotImplementedError(node)

    def visit_DelayStmt(self, node: lal.DelayStmt):
        if isinstance(node.f_has_until, lal.UntilPresent):
            return self._visit_op(OperationNode.Label.DELAYUNTIL, node, OperationNode.Kind.DELAYUNTIL, [node.f_expr])

        return self._visit_op(OperationNode.Label.DELAY, node, OperationNode.Kind.DELAY, [node.f_expr])

    def visit_DeltaAggregate(self, node: lal.DeltaAggregate):
        return self._visit_binop(node, node.f_ancestor_expr, node.f_assocs, op_name=OperationNode.Label.DELTA,
                                 op_kind=OperationNode.Kind.AGGREGATE)

    def visit_DeltaConstraint(self, node: lal.DeltaConstraint):
        raise NotImplementedError(node)

    def visit_DiscreteSubtypeIndication(self, node: lal.DiscreteSubtypeIndication):
        raise NotImplementedError(node)

    def visit_DottedName(self, node: lal.DottedName):
        graph = self.visit(node.f_prefix)

        suffix_name = get_node_full_name(node)
        suffix_key = get_node_key(node)

        try:
            if isinstance(node.p_first_corresponding_decl, lal.PackageDecl):
                kind = DataNode.Kind.PACKAGE_USAGE
            else:
                kind = DataNode.Kind.VARIABLE_USAGE
        except Exception as e:
            print('an exception occurred:', e)
            traceback.print_exc()
            logger.warning(f'Could not determine {node} first corresponding decl')
            kind = DataNode.Kind.VARIABLE_USAGE  # Or undefined?

        data_node = DataNode(self.visitor_helper.get_exas_label(node), node, kind=kind, key=suffix_key)
        graph.add_node(data_node, link_type=LinkType.QUALIFIER, clear_sinks=True)
        return graph

    def visit_ExitStmt(self, node: lal.ExitStmt):
        if node.f_loop_name:
            raise NotImplementedError(node)

        if not node.f_cond_expr:
            return self._visit_dep_resetter(OperationNode.Label.EXIT, node, OperationNode.Kind.EXIT)

        raise NotImplementedError(node)

    def visit_ExplicitDeref(self, node: lal.ExplicitDeref):
        return self._visit_op(OperationNode.Label.DEREFERENCE, node, OperationNode.Kind.DEREFERENCE, [node.f_prefix])

    def visit_ExprAlternativesList(self, node: lal.ExprAlternativesList):
        if len(node) == 1:
            return self.visit(node[0])

        return self._visit_op('|', node, OperationNode.Kind.ALTERNATIVES, node)

    def visit_ExprFunction(self, node: lal.ExprFunction):
        raise NotImplementedError(node)

    def visit_ExtendedReturnStmt(self, node: lal.ExtendedReturnStmt):
        raise NotImplementedError(node)

    def visit_ForLoopSpec(self, node: lal.ForLoopSpec):
        if node.f_iter_filter:
            raise NotImplementedError(node.f_iter_filter)
        return next(self._visit_var_decl([node.f_var_decl], node.f_iter_expr, node.f_has_reverse))

    def visit_ForLoopStmt(self, node: lal.ForLoopStmt):
        control_node = ControlNode(ControlNode.Label.FOR, node, self.control_branch_stack)
        graph = self.visit(node.f_spec)
        graph.add_node(control_node, link_type=LinkType.CONDITION)
        stmts_graph = self._visit_control_node_body(control_node, node.f_stmts, True)
        graph.merge_graph(stmts_graph)
        graph.statement_sinks.clear()
        return graph

    def visit_ForLoopVarDecl(self, node: lal.ForLoopVarDecl):
        raise NotImplementedError(node)

    def visit_GenericSubpInstantiation(self, node: lal.GenericSubpInstantiation):
        raise NotImplementedError(node)  # TODO

    def visit_HandledStmts(self, node: lal.HandledStmts):
        return self.visit(node.f_stmts)

    def visit_Identifier(self, node: lal.Identifier):
        name = get_node_full_name(node)
        key = get_node_key(node)

        if name.lower() == 'true' or name.lower() == 'false':
            return self.create_graph(
                node=DataNode('Boolean', node, kind=DataNode.Kind.LITERAL))

        try:
            if node.p_is_call:
                return self.create_graph(node=OperationNode(name, node, self.control_branch_stack, kind=OperationNode.Kind.FUNC_CALL, key=key))
        except Exception as e:
            logger.warning(f'Could not determine whether {node} is a call.')

        return self._visit_var_usage(node)

    def visit_IfExpr(self, node: lal.IfExpr):
        control_node = ControlNode(ControlNode.Label.IF, node, self.control_branch_stack)
        graph = self.visit(node.f_cond_expr)
        graph.add_node(control_node, link_type=LinkType.CONDITION)

        dummy_node = DataNode(node.__class__.__name__, node, kind=DataNode.Kind.DUMMY_USAGE)

        then_graph = self._visit_control_expr(control_node, node.f_then_expr, True)

        if len(node.f_alternatives):
            else_graph = self._visit_alternatives_expr(control_node, node.f_alternatives.children, node.f_else_expr, False)
        else:
            else_graph = self._visit_control_expr(control_node, node.f_else_expr, False)

        graph.parallel_merge_graphs([then_graph, else_graph])
        graph.add_node(dummy_node, link_type=LinkType.REFERENCE)

        return graph

    def _visit_control_expr(self, control_node, expr, new_branch_kind, replace_control=False):
        self._switch_control_branch(control_node, new_branch_kind, replace=replace_control)
        dummy_node = DataNode(expr.__class__.__name__, expr, kind=DataNode.Kind.DUMMY_DECL)
        graph = self.create_graph()
        graph.add_node(EmptyNode(self.control_branch_stack))
        expr_graph = self.visit(expr)
        sink_nums = []
        for sink in expr_graph.sinks:
            sink.update_property(Node.Property.DEF_FOR, [dummy_node.statement_num])
            sink_nums.append(sink.statement_num)
        dummy_node.set_property(Node.Property.DEF_BY, sink_nums)
        expr_graph.add_node(OperationNode(OperationNode.Label.ASSIGN, expr, self.control_branch_stack, kind=OperationNode.Kind.ASSIGN), link_type=LinkType.PARAMETER)
        expr_graph.add_node(dummy_node, link_type=LinkType.DEFINITION)
        graph.merge_graph(expr_graph)
        self._pop_control_branch()
        return expr_graph

    def _visit_alternatives_expr(self, control_node, alternatives, else_expr, new_branch_kind, replace_control=False):
        self._switch_control_branch(control_node, new_branch_kind, replace=replace_control)
        alternative: lal.ElsifExprPart = alternatives[0]
        remaining_alternatives: list[lal.ElsifExprPart] = alternatives[1:]

        dummy_node = DataNode(alternative.__class__.__name__, alternative, kind=DataNode.Kind.DUMMY_USAGE)

        graph = self.create_graph()
        graph.add_node(EmptyNode(self.control_branch_stack))

        alt_control_node = ControlNode(ControlNode.Label.IF, alternative, self.control_branch_stack)
        conditional_graph = self.visit(alternative.f_cond_expr)
        conditional_graph.add_node(alt_control_node, link_type=LinkType.CONDITION)
        then_graph = self._visit_control_expr(alt_control_node, alternative.f_then_expr, True)
        if len(remaining_alternatives):
            else_graph = self._visit_alternatives_expr(alt_control_node, remaining_alternatives, else_expr, False)
        else:
            else_graph = self._visit_control_expr(alt_control_node, else_expr, False)
        conditional_graph.parallel_merge_graphs([then_graph, else_graph])
        conditional_graph.add_node(dummy_node, link_type=LinkType.REFERENCE)
        graph.merge_graph(conditional_graph)
        self._pop_control_branch()
        return graph

    def visit_IfStmt(self, node: lal.IfStmt):
        control_node = ControlNode(ControlNode.Label.IF, node, self.control_branch_stack)

        graph = self.visit(node.f_cond_expr)
        graph.add_node(control_node, link_type=LinkType.CONDITION)

        then_graph = self._visit_control_node_body(control_node, node.f_then_stmts.children, True)
        if len(node.f_alternatives):
            else_graph = self._visit_alternatives(control_node, list(node.f_alternatives), node.f_else_stmts, False)
        else:
            else_graph = self._visit_control_node_body(control_node, node.f_else_stmts.children or [], False)
        graph.parallel_merge_graphs([then_graph, else_graph])
        return graph

    def visit_IntLiteral(self, node: lal.IntLiteral):
        return self.create_graph(node=DataNode('Integer', node, kind=DataNode.Kind.LITERAL))

    def visit_LoopStmt(self, node: lal.LoopStmt):
        control_node = ControlNode(ControlNode.Label.LOOP, node, self.control_branch_stack)
        graph = self.create_graph(node=control_node)

        stmts_graph = self._visit_control_node_body(control_node, node.f_stmts, True)
        graph.merge_graph(stmts_graph)
        graph.statement_sinks.clear()
        return graph

    def visit_MembershipExpr(self, node: lal.MembershipExpr):
        return self._visit_binop(node, node.f_expr, node.f_membership_exprs,
                                 op_name=node.f_op.__class__.__name__.lower()[2:],
                                 op_kind=OperationNode.Kind.BINARY)

    def visit_NamedStmt(self, node: lal.NamedStmt):
        # TODO: label?
        return self.visit(node.f_stmt)

    def visit_NullLiteral(self, node: lal.NullLiteral):
        return self.create_graph(node=DataNode(self._clear_literal_label(node.text), node, kind=DataNode.Kind.LITERAL))

    def visit_NullStmt(self, node: lal.NullStmt):
        return self.create_graph(node=OperationNode(OperationNode.Label.NULL, node, self.control_branch_stack))

    def visit_NumberDecl(self, node: lal.NumberDecl):
        graph = self.create_graph()
        for decl in self._visit_var_decl(node.f_ids, node.f_expr):
            graph.merge_graph(decl)
        return graph

    def visit_ObjectDecl(self, node: lal.ObjectDecl):
        graph = self.create_graph()
        for decl in self._visit_var_decl(node.f_ids, node.f_default_expr):
            graph.merge_graph(decl)
        return graph

    def visit_OthersDesignator(self, node: lal.OthersDesignator):
        return self.create_graph(node=DataNode(self._clear_literal_label(node.text), node, kind=DataNode.Kind.LITERAL))

    def visit_PackageDecl(self, node: lal.PackageDecl):
        return self.create_graph()

    def visit_ParamAssoc(self, node: lal.ParamAssoc):
        if node.f_designator:
            return self._visit_binop(node, node.f_designator, node.f_r_expr,
                                     op_name='=>',
                                     op_kind=OperationNode.Kind.ASSOCIATION)
        return self.visit(node.f_r_expr)

    def visit_Params(self, node: lal.Params):
        return self.visit(node.f_params)

    def visit_ParamSpec(self, node: lal.ParamSpec):
        return self._visit_var_decl(node.f_ids, node.f_default_expr)

    def visit_ParamSpecList(self, node: lal.ParamSpecList):
        graphs = []
        for param in node:
            graphs.extend(self.visit(param))
        return graphs

    def visit_ParenExpr(self, node: lal.ParenExpr):
        return self.visit(node.f_expr)

    def visit_PragmaNode(self, node: lal.PragmaNode):
        return self.create_graph()

    def visit_QualExpr(self, node: lal.QualExpr):
        return self._visit_op(node.f_prefix.text, node, OperationNode.Kind.QUALIFIEDEXPR, [node.f_suffix])

    def visit_QuantifiedExpr(self, node: lal.QuantifiedExpr):
        self._switch_context(self.context.get_fork())
        op_node = OperationNode(OperationNode.Label.QUANTIFIEDEXPR, node, self.control_branch_stack,
                                kind=OperationNode.Kind.QUANTIFIEDEXPR)
        
        quantifier = self.visit(node.f_quantifier)
        quantifier.add_node(op_node, link_type=LinkType.PARAMETER)

        loop_spec = self.visit(node.f_loop_spec)

        expr = self.visit(node.f_expr)
        expr.add_node(op_node, link_type=LinkType.PARAMETER)

        loop_spec.merge_graph(expr)

        graph = self.create_graph()
        graph.parallel_merge_graphs([quantifier, loop_spec])
        self._pop_context()
        return graph

    def visit_QuantifierAll(self, node: lal.QuantifierAll):
        return self.create_graph(node=DataNode(self._clear_literal_label(node.text), node, kind=DataNode.Kind.QUANTIFIER))

    def visit_QuantifierSome(self, node: lal.QuantifierSome):
        return self.create_graph(node=DataNode(self._clear_literal_label(node.text), node, kind=DataNode.Kind.QUANTIFIER))


    def visit_RaiseStmt(self, node: lal.RaiseStmt):
        return self._visit_dep_resetter(OperationNode.Label.RAISE, node, OperationNode.Kind.RAISE,
                                        reset_variables=True)

    def visit_RealLiteral(self, node: lal.RealLiteral):
        return self.create_graph(node=DataNode('Real', node, kind=DataNode.Kind.LITERAL))

    def visit_RelationOp(self, node: lal.RelationOp):
        return self._visit_binop(node, node.f_left, node.f_right,
                                 op_name=node.f_op.__class__.__name__.lower()[2:],
                                 op_kind=OperationNode.Kind.COMPARE)

    def visit_ReturnStmt(self, node: lal.ReturnStmt):
        return self._visit_dep_resetter(OperationNode.Label.RETURN, node, OperationNode.Kind.RETURN,
                                        reset_variables=True)

    def visit_StmtList(self, node: lal.StmtList):
        graph = self.create_graph()
        for stmt in node.children:
            graph.merge_graph(self.visit(stmt))
        return graph

    def visit_StringLiteral(self, node: lal.StringLiteral):
        return self.create_graph(node=DataNode('String', node, kind=DataNode.Kind.LITERAL))

    def visit_SubpBody(self, node: lal.SubpBody):
        if not self.fg.entry_node:
            return self._visit_entry_node(node)
        raise NotImplementedError(node)

    def visit_SubpSpec(self, node: lal.SubpSpec):
        if node.f_subp_params:
            return self.visit(node.f_subp_params)
        return []

    def visit_SubtypeIndication(self, node: lal.SubtypeIndication):
        if node.f_constraint:
            raise NotImplementedError(node.f_constraint)
        if isinstance(node.f_has_not_null, lal.NotNullPresent):
            raise NotImplementedError(node.f_has_not_null)
        return self.create_graph(node=DataNode(self._clear_literal_label(node.text), node, kind=DataNode.Kind.SUBTYPE_INDICATION))

    def visit_UnOp(self, node: lal.UnOp):
        op_name = node.f_op.__class__.__name__[2:]
        return self._visit_op(op_name, node, OperationNode.Kind.UNARY, [node.f_expr])

    def visit_UsePackageClause(self, node: lal.UsePackageClause):
        return self.create_graph()

    def visit_WhileLoopSpec(self, node: lal.WhileLoopSpec):
        return self.visit(node.f_expr)

    def visit_WhileLoopStmt(self, node: lal.WhileLoopStmt):
        control_node = ControlNode(ControlNode.Label.WHILE, node, self.control_branch_stack)
        graph = self.visit(node.f_spec)
        graph.add_node(control_node, link_type=LinkType.CONDITION)
        stmts_graph = self._visit_control_node_body(control_node, node.f_stmts, True)
        graph.merge_graph(stmts_graph)
        graph.statement_sinks.clear()
        return graph

    def visit_WithClause(self, node: lal.WithClause):
        return self.create_graph()

    @staticmethod
    def _clear_literal_label(label):
        label = str(label).encode('unicode_escape').decode()
        label = html.escape(label[:24])
        return label

    def _visit_alternatives(self, control_node, alternatives, else_stmts, new_branch_kind, replace_control=False):
        self._switch_control_branch(control_node, new_branch_kind, replace=replace_control)
        alternative: lal.ElsifStmtPart = alternatives[0]
        remaining_alternatives: list[lal.ElsifExprPart] = alternatives[1:]
        graph = self.create_graph()
        graph.add_node(EmptyNode(self.control_branch_stack))

        alt_control_node = ControlNode(ControlNode.Label.IF, alternative, self.control_branch_stack)
        conditional_graph = self.visit(alternative.f_cond_expr)
        conditional_graph.add_node(alt_control_node, link_type=LinkType.CONDITION)
        then_graph = self._visit_control_node_body(alt_control_node, alternative.f_stmts, True)
        if len(remaining_alternatives):
            else_graph = self._visit_alternatives(alt_control_node, remaining_alternatives, else_stmts, False)
        else:
            else_graph = self._visit_control_node_body(alt_control_node, else_stmts.children or [], False)
        conditional_graph.parallel_merge_graphs([then_graph, else_graph])
        graph.merge_graph(conditional_graph)
        self._pop_control_branch()
        return graph

    def _visit_binop(self, op, left, right, op_name=None, op_kind=OperationNode.Kind.UNCLASSIFIED):
        return self._visit_op(op_name or op.__class__.__name__.lower(), op, op_kind, [left, right])

    def _visit_control_node_body(self, control_node, statements, new_branch_kind, replace_control=False):
        self._switch_control_branch(control_node, new_branch_kind, replace=replace_control)
        graph = self.create_graph()
        graph.add_node(EmptyNode(self.control_branch_stack))
        for statement in statements:
            graph.merge_graph(self.visit(statement))
        self._pop_control_branch()
        return graph

    # Return/continue/break
    def _visit_dep_resetter(self, label, node, kind, reset_variables=False):
        graph = self.create_graph()

        if getattr(node, 'f_return_expr', None):
            graph.merge_graph(self.visit(node.f_return_expr))

        op_node = OperationNode(label, node, self.control_branch_stack, kind=kind)

        graph.add_node(op_node, link_type=LinkType.PARAMETER)

        graph.statement_sinks.clear()
        if reset_variables:
            self.context.remove_variables(self.control_branch_stack)

        return graph

    def _visit_op(self, op_name, node, op_kind, params):
        op_node = OperationNode(op_name, node, self.control_branch_stack, kind=op_kind)

        param_graphs = []
        for param in params:
            param_graph = self.visit(param)
            param_graph.add_node(op_node, link_type=LinkType.PARAMETER)
            param_graphs.append(param_graph)

        graph = self.create_graph()
        graph.parallel_merge_graphs(param_graphs)
        return graph

    def _visit_subprogram_parameters(self, node: lal.SubpBody):
        param_fgs = []
        for param in node.f_subp_spec.p_params or []:
            if len(param.p_defining_names) == 1:
                for name in param.p_defining_names:
                    raise NotImplementedError('parameters not supported.')
            else:
                raise NotImplementedError('multiple parameters in single paramspec.')

        if not all(param_fgs):
            logger.warning(f'Unsupported args in func def, skipping them...')
            param_fgs = [fg for fg in param_fgs if fg]

        return param_fgs

    def _visit_var_decl(self, names, default_expr, reverse=None):
        for name in names:
            var_name = get_node_full_name(name)
            var_key = get_node_key(name)
            try:
                var_node = DataNode(self.visitor_helper.get_type_expr_label(name.p_basic_decl.f_type_expr),
                                    name, key=var_key, kind=DataNode.Kind.VARIABLE_DECL)
            except Exception as e:
                var_node = DataNode('UNKNOWN', name, key=var_key, kind=DataNode.Kind.VARIABLE_DECL)

            if default_expr:
                op_node = OperationNode(OperationNode.Label.ASSIGN, name, self.control_branch_stack,
                                        kind=OperationNode.Kind.ASSIGN)
                if isinstance(reverse, lal.ReversePresent):
                    graph = self._visit_op('reverse', reverse, OperationNode.Kind.UNARY, [default_expr])
                else:
                    graph = self.visit(default_expr)

                sink_nums = []
                for sink in graph.sinks:
                    sink.update_property(Node.Property.DEF_FOR, [var_node.statement_num])
                    sink_nums.append(sink.statement_num)
                var_node.set_property(Node.Property.DEF_BY, sink_nums)

                graph.add_node(op_node, link_type=LinkType.PARAMETER)
                graph.add_node(var_node, link_type=LinkType.DEFINITION)
            else:
                graph = self.create_graph(node=var_node)

            var_node.set_property(Node.Property.DEF_CONTROL_BRANCH_STACK, self.control_branch_stack)
            self.context.add_variable(var_node)

            yield graph

    def _visit_var_usage(self, node: lal.Identifier):
        var_name = get_node_full_name(node)
        var_key = get_node_key(node)
        graph = self.create_graph()
        try:
            if isinstance(node.p_first_corresponding_decl, lal.PackageDecl):
                kind = DataNode.Kind.PACKAGE_USAGE
            else:
                kind = DataNode.Kind.VARIABLE_USAGE
        except Exception as e:
            print('an exception occurred:', e)
            traceback.print_exc()
            logging.debug('Could not determine first corresponding decl')
            kind = DataNode.Kind.VARIABLE_USAGE
        try:
            if node.p_first_corresponding_decl:
                if node.p_first_corresponding_decl.f_type_expr:
                    graph.add_node(DataNode(self.visitor_helper.get_type_expr_label(node.p_first_corresponding_decl.f_type_expr),
                                            node, key=var_key, kind=kind))
            graph.add_node(DataNode(node.text, node, key=var_key, kind=kind))
        except Exception as e:
            print('an exception occurred:', e)
            traceback.print_exc()
            graph.add_node(DataNode(node.text, node, key=var_key, kind=kind))
        return graph
