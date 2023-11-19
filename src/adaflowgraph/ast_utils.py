import libadalang as lal


def get_node_key(node: lal.AdaNode):
    if isinstance(node, lal.AttributeRef):
        return node.text
    elif isinstance(node, lal.Identifier):
        return node.text
    elif isinstance(node, lal.CallExpr):
        return get_node_key(node.f_name)
    elif isinstance(node, lal.DefiningName):
        return get_node_key(node.f_name)
    elif isinstance(node, lal.DottedName):
        return node.text
    elif isinstance(node, lal.ExplicitDeref):
        return node.text
    elif isinstance(node, lal.ForLoopVarDecl):
        return get_node_key(node.f_id)
    raise NotImplementedError(node)


def get_node_full_name(node: lal.AdaNode):
    if isinstance(node, lal.Identifier):
        return node.text
    elif isinstance(node, lal.CallExpr):
        return get_node_full_name(node.f_name)
    elif isinstance(node, lal.DefiningName):
        return get_node_full_name(node.f_name)
    elif isinstance(node, lal.DottedName):
        return node.text
    elif isinstance(node, lal.ExplicitDeref):
        return node.text
    elif isinstance(node, lal.ForLoopVarDecl):
        return get_node_full_name(node.f_id)
    raise NotImplementedError(node)


def get_node_short_name(node: lal.AdaNode):
    if isinstance(node, lal.AttributeRef):
        return get_node_short_name(node.f_attribute)
    elif isinstance(node, lal.Identifier):
        return node.text
    elif isinstance(node, lal.CallExpr):
        return get_node_short_name(node.f_name)
    elif isinstance(node, lal.DefiningName):
        return get_node_short_name(node.f_name)
    elif isinstance(node, lal.DottedName):
        return node.text
    elif isinstance(node, lal.ExplicitDeref):
        return node.text
    elif isinstance(node, lal.ForLoopVarDecl):
        return get_node_short_name(node.f_id)
    raise NotImplementedError(node)
