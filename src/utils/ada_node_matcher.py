from typing import Optional

from libadalang import *
from multimethod import multimethod


@multimethod
def match(node1: Optional[AdaNode], node2: Optional[AdaNode]) -> bool:
    if node1 is None and node2 is None:
        return True
    elif node1 is None or node2 is None:
        return False
    elif node1.kind_name != node2.kind_name:
        return False
    return match_specific(node1, node2)


@multimethod
def match(nodes1: list[AdaNode], nodes2: list[AdaNode]) -> bool:
    if len(nodes1) != len(nodes2):
        return False
    for i, _ in enumerate(nodes1):
        if not match(nodes1[i], nodes2[i]):
            return False
    return True


@multimethod
def match_specific(node1: AdaNode, node2: AdaNode):
    raise NotImplementedError('match_specific {} not implemented!'.format(node1.kind_name))


# 1: AbortAbsent
# 2: AbortPresent
# 3: AbstractAbsent
# 4: AbstractPresent

#  5 .. 33: Lists
@multimethod
def match_specific(node1: AdaList, node2: AdaList) -> bool:
    return match(node1.children, node2.children)


#  34: AliasedAbsent TODO: check if this is correct
@multimethod
def match_specific(node1: AliasedAbsent, node2: AliasedAbsent) -> bool:
    return True


#  35: AliasedPresent TODO: check if this is correct
@multimethod
def match_specific(node1: AliasedPresent, node2: AliasedPresent) -> bool:
    return True


#  36: AllAbsent TODO: check if this is correct
@multimethod
def match_specific(node1: AllAbsent, node2: AllAbsent) -> bool:
    return True


#  37: AllPresent TODO: check if this is correct
@multimethod
def match_specific(node1: AllPresent, node2: AllPresent) -> bool:
    return True


#  38: ConstrainedArrayIndices
@multimethod
def match_specific(node1: ConstrainedArrayIndices, node2: ConstrainedArrayIndices) -> bool:
    return match(node1.f_list, node2.f_list)


#  39: UnconstrainedArrayIndices
@multimethod
def match_specific(node1: UnconstrainedArrayIndices, node2: UnconstrainedArrayIndices) -> bool:
    return match(node1.f_types, node2.f_types)


#  40: AspectAssoc
@multimethod
def match_specific(node1: AspectAssoc, node2: AspectAssoc) -> bool:
    return match(node1.f_id, node2.f_id) \
           and match(node1.f_expr, node2.f_expr)


#  41: AtClause
@multimethod
def match_specific(node1: AtClause, node2: AtClause) -> bool:
    return match(node1.f_name, node2.f_name) \
           and match(node1.f_expr, node2.f_expr)


#  42: AttributeDefClause
@multimethod
def match_specific(node1: AttributeDefClause, node2: AttributeDefClause) -> bool:
    return match(node1.f_attribute_expr, node2.f_attribute_expr) \
           and match(node1.f_expr, node2.f_expr)


#  43: EnumRepClause
@multimethod
def match_specific(node1: EnumRepClause, node2: EnumRepClause) -> bool:
    return match(node1.f_type_name, node2.f_type_name) \
           and match(node1.f_aggregate, node2.f_aggregate)


#  44: RecordRepClause
@multimethod
def match_specific(node1: RecordRepClause, node2: RecordRepClause) -> bool:
    return match(node1.f_name, node2.f_name) \
           and match(node1.f_at_expr, node2.f_at_expr) \
           and match(node1.f_components, node2.f_components)


#  45: AspectSpec
@multimethod
def match_specific(node1: AspectSpec, node2: AspectSpec) -> bool:
    return match(node1.f_aspect_assocs, node2.f_aspect_assocs)


#  46: ContractCaseAssoc
@multimethod
def match_specific(node1: ContractCaseAssoc, node2: ContractCaseAssoc) -> bool:
    return match(node1.f_guard, node2.f_guard) \
           and match(node1.f_consequence, node2.f_consequence)


#  47: PragmaArgumentAssoc
@multimethod
def match_specific(node1: PragmaArgumentAssoc, node2: PragmaArgumentAssoc) -> bool:
    return match(node1.f_name, node2.f_name) \
           and match(node1.f_expr, node2.f_expr)


#  48: EntrySpec
@multimethod
def match_specific(node1: EntrySpec, node2: EntrySpec) -> bool:
    return match(node1.f_entry_name, node2.f_entry_name) \
           and match(node1.f_family_type, node2.f_family_type) \
           and match(node1.f_entry_params, node2.f_entry_params)


#  50: SubpSpec
@multimethod
def match_specific(node1: SubpSpec, node2: SubpSpec) -> bool:
    return match(node1.f_subp_kind, node2.f_subp_kind) \
           and match(node1.f_subp_name, node2.f_subp_name) \
           and match(node1.f_subp_params, node2.f_subp_params) \
           and match(node1.f_subp_returns, node2.f_subp_returns)


#  51: SyntheticBinarySpec
@multimethod
def match_specific(node1: SyntheticBinarySpec, node2: SyntheticBinarySpec) -> bool:
    return match(node1.f_left_param, node2.f_left_param) \
           and match(node1.f_right_param, node2.f_right_param) \
           and match(node1.f_return_type_expr, node2.f_return_type_expr)


#  52: SyntheticUnarySpec
@multimethod
def match_specific(node1: SyntheticUnarySpec, node2: SyntheticUnarySpec) -> bool:
    return match(node1.f_right_param, node2.f_right_param) \
           and match(node1.f_return_type_expr, node2.f_return_type_expr)


#  53: ComponentList
@multimethod
def match_specific(node1: ComponentList, node2: ComponentList) -> bool:
    return match(node1.f_components, node2.f_components) \
           and match(node1.f_variant_part, node2.f_variant_part)


#  54: KnownDiscriminantPart
@multimethod
def match_specific(node1: KnownDiscriminantPart, node2: KnownDiscriminantPart) -> bool:
    return match(node1.f_discr_specs, node2.f_discr_specs)


#  56: EntryCompletionFormalParams
@multimethod
def match_specific(node1: EntryCompletionFormalParams, node2: EntryCompletionFormalParams) -> bool:
    return match(node1.f_params, node2.f_params)


#  57: GenericFormalPart
@multimethod
def match_specific(node1: GenericFormalPart, node2: GenericFormalPart) -> bool:
    return match(node1.f_decls, node2.f_decls)


#  58: NullRecordDef
@multimethod
def match_specific(node1: NullRecordDef, node2: NullRecordDef) -> bool:
    return match(node1.f_components, node2.f_components)


#  59: RecordDef
@multimethod
def match_specific(node1: RecordDef, node2: RecordDef) -> bool:
    return match(node1.f_components, node2.f_components)


#  60: AggregateAssoc
@multimethod
def match_specific(node1: AggregateAssoc, node2: AggregateAssoc) -> bool:
    return match(node1.f_designators, node2.f_designators) \
           and match(node1.f_r_expr, node2.f_r_expr)


#  61: MultiDimArrayAssoc
@multimethod
def match_specific(node1: MultiDimArrayAssoc, node2: MultiDimArrayAssoc) -> bool:
    return match(node1.f_designators, node2.f_designators) \
           and match(node1.f_r_expr, node2.f_r_expr)


#  62: CompositeConstraintAssoc
@multimethod
def match_specific(node1: CompositeConstraintAssoc, node2: CompositeConstraintAssoc) -> bool:
    return match(node1.f_ids, node2.f_ids) \
           and match(node1.f_constraint_expr, node2.f_constraint_expr)


#  63: IteratedAssoc
@multimethod
def match_specific(node1: IteratedAssoc, node2: IteratedAssoc) -> bool:
    return match(node1.f_spec, node2.f_spec) \
           and match(node1.f_r_expr, node2.f_r_expr)


#  64: ParamAssoc
@multimethod
def match_specific(node1: ParamAssoc, node2: ParamAssoc) -> bool:
    return match(node1.f_designator, node2.f_designator) \
           and match(node1.f_r_expr, node2.f_r_expr)


#  65: AbstractStateDecl
@multimethod
def match_specific(node1: AbstractStateDecl, node2: AbstractStateDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_name, node2.f_name)


#  66: AnonymousExprDecl
@multimethod
def match_specific(node1: AnonymousExprDecl, node2: AnonymousExprDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_expr, node2.f_expr)


# 67: ComponentDecl
@multimethod
def match_specific(node1: ComponentDecl, node2: ComponentDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_ids, node2.f_ids) \
           and match(node1.f_component_def, node2.f_component_def) \
           and match(node1.f_default_expr, node2.f_default_expr)


#  68: DiscriminantSpec
@multimethod
def match_specific(node1: DiscriminantSpec, node2: DiscriminantSpec) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_ids, node2.f_ids) \
           and match(node1.f_type_expr, node2.f_type_expr) \
           and match(node1.f_default_expr, node2.f_default_expr)


#  69: GenericFormalObjDecl
@multimethod
def match_specific(node1: GenericFormalObjDecl, node2: GenericFormalObjDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_decl, node2.f_decl)


#  70: GenericFormalPackage
@multimethod
def match_specific(node1: GenericFormalPackage, node2: GenericFormalPackage) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_decl, node2.f_decl)


#  71: GenericFormalSubpDecl
@multimethod
def match_specific(node1: GenericFormalSubpDecl, node2: GenericFormalSubpDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_decl, node2.f_decl)


#  72: GenericFormalTypeDecl
@multimethod
def match_specific(node1: GenericFormalTypeDecl, node2: GenericFormalTypeDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_decl, node2.f_decl)


#  73: ParamSpec
@multimethod
def match_specific(node1: ParamSpec, node2: ParamSpec) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_ids, node2.f_ids) \
           and match(node1.f_has_aliased, node2.f_has_aliased) \
           and match(node1.f_mode, node2.f_mode) \
           and match(node1.f_type_expr, node2.f_type_expr) \
           and match(node1.f_default_expr, node2.f_default_expr)


#  74: SyntheticFormalParamDecl
@multimethod
def match_specific(node1: SyntheticFormalParamDecl, node2: SyntheticFormalParamDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_param_type, node2.f_param_type)


#  75: GenericPackageInternal
@multimethod
def match_specific(node1: GenericPackageInternal, node2: GenericPackageInternal) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_package_name, node2.f_package_name) \
           and match(node1.f_public_part, node2.f_public_part) \
           and match(node1.f_private_part, node2.f_private_part) \
           and match(node1.f_end_name, node2.f_end_name)


#  76: PackageDecl
@multimethod
def match_specific(node1: PackageDecl, node2: PackageDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_package_name, node2.f_package_name) \
           and match(node1.f_public_part, node2.f_public_part) \
           and match(node1.f_private_part, node2.f_private_part) \
           and match(node1.f_end_name, node2.f_end_name)


#  77: DiscreteBaseSubtypeDecl
@multimethod
def match_specific(node1: DiscreteBaseSubtypeDecl, node2: DiscreteBaseSubtypeDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_name, node2.f_name)


#  78: SubtypeDecl
@multimethod
def match_specific(node1: SubtypeDecl, node2: SubtypeDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_name, node2.f_name) \
           and match(node1.f_subtype, node2.f_subtype)


#  79: ClasswideTypeDecl
@multimethod
def match_specific(node1: ClasswideTypeDecl, node2: ClasswideTypeDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_name, node2.f_name)


# 80: IncompleteTypeDecl
@multimethod
def match_specific(node1: IncompleteTypeDecl, node2: IncompleteTypeDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_name, node2.f_name) \
           and match(node1.f_discriminants, node2.f_discriminants)


#  81: IncompleteFormalTypeDecl
@multimethod
def match_specific(node1: IncompleteFormalTypeDecl, node2: IncompleteFormalTypeDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_name, node2.f_name) \
           and match(node1.f_discriminants, node2.f_discriminants) \
           and match(node1.f_is_tagged, node2.f_is_tagged) \
           and match(node1.f_default_type, node2.f_default_type)


# 82: IncompleteTaggedTypeDecl
@multimethod
def match_specific(node1: IncompleteTaggedTypeDecl, node2: IncompleteTaggedTypeDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_name, node2.f_name) \
           and match(node1.f_discriminants, node2.f_discriminants) \
           and match(node1.f_has_abstract, node2.f_has_abstract)


#  83: ProtectedTypeDecl
@multimethod
def match_specific(node1: ProtectedTypeDecl, node2: ProtectedTypeDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_name, node2.f_name) \
           and match(node1.f_discriminants, node2.f_discriminants) \
           and match(node1.f_definition, node2.f_definition)


#  84: TaskTypeDecl
@multimethod
def match_specific(node1: TaskTypeDecl, node2: TaskTypeDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_name, node2.f_name) \
           and match(node1.f_definition, node2.f_definition)


#  85: SingleTaskTypeDecl
@multimethod
def match_specific(node1: SingleTaskTypeDecl, node2: SingleTaskTypeDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_name, node2.f_name) \
           and match(node1.f_discriminants, node2.f_discriminants) \
           and match(node1.f_definition, node2.f_definition)


#  86: AnonymousTypeDecl
@multimethod
def match_specific(node1: AnonymousTypeDecl, node2: AnonymousTypeDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_name, node2.f_name) \
           and match(node1.f_discriminants, node2.f_discriminants) \
           and match(node1.f_type_def, node2.f_type_def)


#  87: SynthAnonymousTypeDecl
@multimethod
def match_specific(node1: SynthAnonymousTypeDecl, node2: SynthAnonymousTypeDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_name, node2.f_name) \
           and match(node1.f_discriminants, node2.f_discriminants) \
           and match(node1.f_type_def, node2.f_type_def)


#  88: ConcreteTypeDecl
@multimethod
def match_specific(node1: ConcreteTypeDecl, node2: ConcreteTypeDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_name, node2.f_name) \
           and match(node1.f_discriminants, node2.f_discriminants) \
           and match(node1.f_type_def, node2.f_type_def)


#  89: FormalTypeDecl
@multimethod
def match_specific(node1: FormalTypeDecl, node2: FormalTypeDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_name, node2.f_name) \
           and match(node1.f_discriminants, node2.f_discriminants) \
           and match(node1.f_type_def, node2.f_type_def) \
           and match(node1.f_default_type, node2.f_default_type)


#  90: AbstractSubpDecl
@multimethod
def match_specific(node1: AbstractSubpDecl, node2: AbstractSubpDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_overriding, node2.f_overriding) \
           and match(node1.f_subp_spec, node2.f_subp_spec)


#  91: AbstractFormalSubpDecl
@multimethod
def match_specific(node1: AbstractFormalSubpDecl, node2: AbstractFormalSubpDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_overriding, node2.f_overriding) \
           and match(node1.f_subp_spec, node2.f_subp_spec) \
           and match(node1.f_default_expr, node2.f_default_expr)


#  92: ConcreteFormalSubpDecl
@multimethod
def match_specific(node1: ConcreteFormalSubpDecl, node2: ConcreteFormalSubpDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_overriding, node2.f_overriding) \
           and match(node1.f_subp_spec, node2.f_subp_spec) \
           and match(node1.f_default_expr, node2.f_default_expr)


#  93: SubpDecl
@multimethod
def match_specific(node1: SubpDecl, node2: SubpDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_overriding, node2.f_overriding) \
           and match(node1.f_subp_spec, node2.f_subp_spec)


#  94: EntryDecl
@multimethod
def match_specific(node1: EntryDecl, node2: EntryDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_overriding, node2.f_overriding) \
           and match(node1.f_spec, node2.f_spec)


#  95: EnumLiteralDecl
@multimethod
def match_specific(node1: EnumLiteralDecl, node2: EnumLiteralDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_name, node2.f_name)


#  96: SyntheticCharEnumLit
@multimethod
def match_specific(node1: SyntheticCharEnumLit, node2: SyntheticCharEnumLit) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_name, node2.f_name)


# 97: GenericSubpInternal
@multimethod
def match_specific(node1: GenericSubpInternal, node2: GenericSubpInternal) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_subp_spec, node2.f_subp_spec)


# 98: SyntheticSubpDecl
@multimethod
def match_specific(node1: SyntheticSubpDecl, node2: SyntheticSubpDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_spec, node2.f_spec)


# 99: ExprFunction
@multimethod
def match_specific(node1: ExprFunction, node2: ExprFunction) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_overriding, node2.f_overriding) \
           and match(node1.f_subp_spec, node2.f_subp_spec) \
           and match(node1.f_expr, node2.f_expr)


# 100: NullSubpDecl
@multimethod
def match_specific(node1: NullSubpDecl, node2: NullSubpDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_overriding, node2.f_overriding) \
           and match(node1.f_subp_spec, node2.f_subp_spec)


# 101: SubpBody
@multimethod
def match_specific(node1: SubpBody, node2: SubpBody) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_overriding, node2.f_overriding) \
           and match(node1.f_subp_spec, node2.f_subp_spec) \
           and match(node1.f_decls, node2.f_decls) \
           and match(node1.f_stmts, node2.f_stmts) \
           and match(node1.f_end_name, node2.f_end_name)


# 102: SubpRenamingDecl
@multimethod
def match_specific(node1: SubpRenamingDecl, node2: SubpRenamingDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_overriding, node2.f_overriding) \
           and match(node1.f_subp_spec, node2.f_subp_spec) \
           and match(node1.f_renames, node2.f_renames)


# 103: PackageBodyStub
@multimethod
def match_specific(node1: PackageBodyStub, node2: PackageBodyStub) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_name, node2.f_name)


# 104: ProtectedBodyStub
@multimethod
def match_specific(node1: ProtectedBodyStub, node2: ProtectedBodyStub) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_name, node2.f_name)


# 105: SubpBodyStub
@multimethod
def match_specific(node1: SubpBodyStub, node2: SubpBodyStub) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_overriding, node2.f_overriding) \
           and match(node1.f_subp_spec, node2.f_subp_spec)


# 106: TaskBodyStub
@multimethod
def match_specific(node1: TaskBodyStub, node2: TaskBodyStub) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_name, node2.f_name)


# 107: EntryBody
@multimethod
def match_specific(node1: EntryBody, node2: EntryBody) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_entry_name, node2.f_entry_name) \
           and match(node1.f_index_spec, node2.f_index_spec) \
           and match(node1.f_params, node2.f_params) \
           and match(node1.f_barrier, node2.f_barrier) \
           and match(node1.f_decls, node2.f_decls) \
           and match(node1.f_stmts, node2.f_stmts) \
           and match(node1.f_end_name, node2.f_end_name)


# 108: PackageBody
@multimethod
def match_specific(node1: PackageBody, node2: PackageBody) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_package_name, node2.f_package_name) \
           and match(node1.f_decls, node2.f_decls) \
           and match(node1.f_stmts, node2.f_stmts) \
           and match(node1.f_end_name, node2.f_end_name)


# 109: ProtectedBody
@multimethod
def match_specific(node1: ProtectedBody, node2: ProtectedBody) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_name, node2.f_name) \
           and match(node1.f_decls, node2.f_decls) \
           and match(node1.f_end_name, node2.f_end_name)


# 110: TaskBody
@multimethod
def match_specific(node1: TaskBody, node2: TaskBody) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_name, node2.f_name) \
           and match(node1.f_decls, node2.f_decls) \
           and match(node1.f_stmts, node2.f_stmts) \
           and match(node1.f_end_name, node2.f_end_name)


# 111: EntryIndexSpec
@multimethod
def match_specific(node1: EntryIndexSpec, node2: EntryIndexSpec) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_id, node2.f_id) \
           and match(node1.f_subtype, node2.f_subtype)


# 112: ErrorDecl
@multimethod
def match_specific(node1: ErrorDecl, node2: ErrorDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects)


# 113: ExceptionDecl
@multimethod
def match_specific(node1: ExceptionDecl, node2: ExceptionDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_ids, node2.f_ids) \
           and match(node1.f_renames, node2.f_renames)


# 114: ExceptionHandler
@multimethod
def match_specific(node1: ExceptionHandler, node2: ExceptionHandler) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_exception_name, node2.f_exception_name) \
           and match(node1.f_handled_exceptions, node2.f_handled_exceptions) \
           and match(node1.f_stmts, node2.f_stmts)


# 115: ForLoopVarDecl
@multimethod
def match_specific(node1: ForLoopVarDecl, node2: ForLoopVarDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_id, node2.f_id) \
           and match(node1.f_id_type, node2.f_id_type)


# 116: GenericPackageDecl
@multimethod
def match_specific(node1: GenericPackageDecl, node2: GenericPackageDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_formal_part, node2.f_formal_part) \
           and match(node1.f_package_decl, node2.f_package_decl)


# 117: GenericSubpDecl
@multimethod
def match_specific(node1: GenericSubpDecl, node2: GenericSubpDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_formal_part, node2.f_formal_part) \
           and match(node1.f_subp_decl, node2.f_subp_decl)


# 118: GenericPackageInstantiation
@multimethod
def match_specific(node1: GenericPackageInstantiation, node2: GenericPackageInstantiation) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_name, node2.f_name) \
           and match(node1.f_generic_pkg_name, node2.f_generic_pkg_name) \
           and match(node1.f_params, node2.f_params)


# 119: GenericSubpInstantiation
@multimethod
def match_specific(node1: GenericSubpInstantiation, node2: GenericSubpInstantiation) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_overriding, node2.f_overriding) \
           and match(node1.f_kind, node2.f_kind) \
           and match(node1.f_subp_name, node2.f_subp_name) \
           and match(node1.f_generic_subp_name, node2.f_generic_subp_name) \
           and match(node1.f_params, node2.f_params)


# 120: GenericPackageRenamingDecl
@multimethod
def match_specific(node1: GenericPackageRenamingDecl, node2: GenericPackageRenamingDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_name, node2.f_name) \
           and match(node1.f_renames, node2.f_renames)


# 121: GenericSubpRenamingDecl
@multimethod
def match_specific(node1: GenericSubpRenamingDecl, node2: GenericSubpRenamingDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_kind, node2.f_kind) \
           and match(node1.f_name, node2.f_name) \
           and match(node1.f_renames, node2.f_renames)


# 122: LabelDecl
@multimethod
def match_specific(node1: LabelDecl, node2: LabelDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_name, node2.f_name)


# 123: NamedStmtDecl
@multimethod
def match_specific(node1: NamedStmtDecl, node2: NamedStmtDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_name, node2.f_name)


# 124: NumberDecl
@multimethod
def match_specific(node1: NumberDecl, node2: NumberDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_ids, node2.f_ids) \
           and match(node1.f_expr, node2.f_expr)


# 125: ObjectDecl
@multimethod
def match_specific(node1: ObjectDecl, node2: ObjectDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_ids, node2.f_ids) \
           and match(node1.f_has_aliased, node2.f_has_aliased) \
           and match(node1.f_has_constant, node2.f_has_constant) \
           and match(node1.f_mode, node2.f_mode) \
           and match(node1.f_type_expr, node2.f_type_expr) \
           and match(node1.f_default_expr, node2.f_default_expr) \
           and match(node1.f_renaming_clause, node2.f_renaming_clause)


# 126: ExtendedReturnStmtObjectDecl
@multimethod
def match_specific(node1: ExtendedReturnStmtObjectDecl, node2: ExtendedReturnStmtObjectDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_ids, node2.f_ids) \
           and match(node1.f_has_aliased, node2.f_has_aliased) \
           and match(node1.f_has_constant, node2.f_has_constant) \
           and match(node1.f_mode, node2.f_mode) \
           and match(node1.f_type_expr, node2.f_type_expr) \
           and match(node1.f_default_expr, node2.f_default_expr) \
           and match(node1.f_renaming_clause, node2.f_renaming_clause)


# 127: NoTypeObjectRenamingDecl
@multimethod
def match_specific(node1: NoTypeObjectRenamingDecl, node2: NoTypeObjectRenamingDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_ids, node2.f_ids) \
           and match(node1.f_has_aliased, node2.f_has_aliased) \
           and match(node1.f_has_constant, node2.f_has_constant) \
           and match(node1.f_mode, node2.f_mode) \
           and match(node1.f_type_expr, node2.f_type_expr) \
           and match(node1.f_default_expr, node2.f_default_expr) \
           and match(node1.f_renaming_clause, node2.f_renaming_clause)


# 128: PackageRenamingDecl
@multimethod
def match_specific(node1: PackageRenamingDecl, node2: PackageRenamingDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_name, node2.f_name) \
           and match(node1.f_renames, node2.f_renames)


# 129: SingleProtectedDecl
@multimethod
def match_specific(node1: SingleProtectedDecl, node2: SingleProtectedDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_name, node2.f_name) \
           and match(node1.f_interfaces, node2.f_interfaces) \
           and match(node1.f_definition, node2.f_definition)


# 130: SingleTaskDecl
@multimethod
def match_specific(node1: SingleTaskDecl, node2: SingleTaskDecl) -> bool:
    return match(node1.f_aspects, node2.f_aspects) \
           and match(node1.f_task_type, node2.f_task_type)


# 131: CaseStmtAlternative
@multimethod
def match_specific(node1: CaseStmtAlternative, node2: CaseStmtAlternative) -> bool:
    return match(node1.f_choices, node2.f_choices) \
           and match(node1.f_stmts, node2.f_stmts)


# 132: CompilationUnit
@multimethod
def match_specific(node1: CompilationUnit, node2: CompilationUnit) -> bool:
    return match(node1.f_prelude, node2.f_prelude) \
           and match(node1.f_body, node2.f_body) \
           and match(node1.f_pragmas, node2.f_pragmas)


# 133: ComponentClause
@multimethod
def match_specific(node1: ComponentClause, node2: ComponentClause) -> bool:
    return match(node1.f_id, node2.f_id) \
           and match(node1.f_position, node2.f_position) \
           and match(node1.f_range, node2.f_range)


# 134: ComponentDef
@multimethod
def match_specific(node1: ComponentDef, node2: ComponentDef) -> bool:
    return match(node1.f_has_aliased, node2.f_has_aliased) \
           and match(node1.f_has_constant, node2.f_has_constant) \
           and match(node1.f_type_expr, node2.f_type_expr)


# 135: ConstantAbsent TODO: check if this is correct
@multimethod
def match_specific(node1: ConstantAbsent, node2: ConstantAbsent) -> bool:
    return True


# 136: ConstantPresent TODO: check if this is correct
@multimethod
def match_specific(node1: ConstantPresent, node2: ConstantPresent) -> bool:
    return True


# 137: CompositeConstraint
@multimethod
def match_specific(node1: CompositeConstraint, node2: CompositeConstraint) -> bool:
    return match(node1.f_constraints, node2.f_constraints)


# 138: DeltaConstraint
@multimethod
def match_specific(node1: DeltaConstraint, node2: DeltaConstraint) -> bool:
    return match(node1.f_digits, node2.f_digits) \
           and match(node1.f_range, node2.f_range)


# 139: DigitsConstraint
@multimethod
def match_specific(node1: DigitsConstraint, node2: DigitsConstraint) -> bool:
    return match(node1.f_digits, node2.f_digits) \
           and match(node1.f_range, node2.f_range)


# 140: RangeConstraint
@multimethod
def match_specific(node1: RangeConstraint, node2: RangeConstraint) -> bool:
    return match(node1.f_range, node2.f_range)


# 141: DeclarativePart
@multimethod
def match_specific(node1: DeclarativePart, node2: DeclarativePart) -> bool:
    return match(node1.f_decls, node2.f_decls)


# 142: PrivatePart
@multimethod
def match_specific(node1: PrivatePart, node2: PrivatePart) -> bool:
    return match(node1.f_decls, node2.f_decls)


# 143: PublicPart
@multimethod
def match_specific(node1: PublicPart, node2: PublicPart) -> bool:
    return match(node1.f_decls, node2.f_decls)


# 144: ElsifExprPart
@multimethod
def match_specific(node1: ElsifExprPart, node2: ElsifExprPart) -> bool:
    return match(node1.f_cond_expr, node2.f_cond_expr) \
           and match(node1.f_then_expr, node2.f_then_expr)


# 145: ElsifStmtPart
@multimethod
def match_specific(node1: ElsifStmtPart, node2: ElsifStmtPart) -> bool:
    return match(node1.f_cond_expr, node2.f_cond_expr) \
           and match(node1.f_stmts, node2.f_stmts)


# 146: AbstractStateDeclExpr
@multimethod
def match_specific(node1: AbstractStateDeclExpr, node2: AbstractStateDeclExpr) -> bool:
    return match(node1.f_state_decl, node2.f_state_decl)


# 147: Allocator
@multimethod
def match_specific(node1: Allocator, node2: Allocator) -> bool:
    return match(node1.f_subpool, node2.f_subpool) \
           and match(node1.f_type_or_expr, node2.f_type_or_expr)


# 148: Aggregate
@multimethod
def match_specific(node1: Aggregate, node2: Aggregate) -> bool:
    return match(node1.f_ancestor_expr, node2.f_ancestor_expr) \
           and match(node1.f_assocs, node2.f_assocs)


# 149: BracketAggregate
@multimethod
def match_specific(node1: BracketAggregate, node2: BracketAggregate) -> bool:
    return match(node1.f_ancestor_expr, node2.f_ancestor_expr) \
           and match(node1.f_assocs, node2.f_assocs)


# 150: DeltaAggregate
@multimethod
def match_specific(node1: DeltaAggregate, node2: DeltaAggregate) -> bool:
    return match(node1.f_ancestor_expr, node2.f_ancestor_expr) \
           and match(node1.f_assocs, node2.f_assocs)


# 151: BracketDeltaAggregate
@multimethod
def match_specific(node1: BracketDeltaAggregate, node2: BracketDeltaAggregate) -> bool:
    return match(node1.f_ancestor_expr, node2.f_ancestor_expr) \
           and match(node1.f_assocs, node2.f_assocs)


# 152: NullRecordAggregate
@multimethod
def match_specific(node1: NullRecordAggregate, node2: NullRecordAggregate) -> bool:
    return match(node1.f_ancestor_expr, node2.f_ancestor_expr) \
           and match(node1.f_assocs, node2.f_assocs)


# 153: BinOp
@multimethod
def match_specific(node1: BinOp, node2: BinOp) -> bool:
    return match(node1.f_left, node2.f_left) \
           and match(node1.f_op, node2.f_op) \
           and match(node1.f_right, node2.f_right)


# 154: RelationOp
@multimethod
def match_specific(node1: RelationOp, node2: RelationOp) -> bool:
    return match(node1.f_left, node2.f_left) \
           and match(node1.f_op, node2.f_op) \
           and match(node1.f_right, node2.f_right)


# 155: BoxExpr
@multimethod
def match_specific(node1: BoxExpr, node2: BoxExpr) -> bool:
    return True


# 156: CaseExprAlternative
@multimethod
def match_specific(node1: CaseExprAlternative, node2: CaseExprAlternative) -> bool:
    return match(node1.f_choices, node2.f_choices) \
           and match(node1.f_expr, node2.f_expr)


# 157: ConcatOp
@multimethod
def match_specific(node1: ConcatOp, node2: ConcatOp) -> bool:
    return match(node1.f_first_operand, node2.f_first_operand) \
           and match(node1.f_other_operands, node2.f_other_operands)


# 158: ConcatOperand
@multimethod
def match_specific(node1: ConcatOperand, node2: ConcatOperand) -> bool:
    return match(node1.f_operator, node2.f_operator) \
           and match(node1.f_operand, node2.f_operand)


# 159: CaseExpr
@multimethod
def match_specific(node1: CaseExpr, node2: CaseExpr) -> bool:
    return match(node1.f_expr, node2.f_expr) \
           and match(node1.f_cases, node2.f_cases)


# 160: IfExpr
@multimethod
def match_specific(node1: IfExpr, node2: IfExpr) -> bool:
    return match(node1.f_cond_expr, node2.f_cond_expr) and \
           match(node1.f_then_expr, node2.f_then_expr) and \
           match(node1.f_alternatives, node2.f_alternatives) and \
           match(node1.f_else_expr, node2.f_else_expr)


# 161: ContractCases
@multimethod
def match_specific(node1: ContractCases, node2: ContractCases) -> bool:
    return match(node1.f_contract_cases, node2.f_contract_cases)


# 162: DeclExpr
@multimethod
def match_specific(node1: DeclExpr, node2: DeclExpr) -> bool:
    return match(node1.f_decls, node2.f_decls) \
           and match(node1.f_expr, node2.f_expr)


# 163: MembershipExpr
@multimethod
def match_specific(node1: MembershipExpr, node2: MembershipExpr) -> bool:
    return match(node1.f_expr, node2.f_expr) \
           and match(node1.f_op, node2.f_op) \
           and match(node1.f_membership_exprs, node2.f_membership_exprs)


# 164: AttributeRef
@multimethod
def match_specific(node1: AttributeRef, node2: AttributeRef) -> bool:
    return match(node1.f_prefix, node2.f_prefix) \
           and match(node1.f_attribute, node2.f_attribute) \
           and match(node1.f_args, node2.f_args)


# 165: CallExpr
@multimethod
def match_specific(node1: CallExpr, node2: CallExpr) -> bool:
    return match(node1.f_name, node2.f_name) \
           and match(node1.f_suffix, node2.f_suffix)


# 166: DefiningName
@multimethod
def match_specific(node1: DefiningName, node2: DefiningName) -> bool:
    return match(node1.f_name, node2.f_name)


# 167: SyntheticDefiningName
@multimethod
def match_specific(node1: SyntheticDefiningName, node2: SyntheticDefiningName) -> bool:
    return match(node1.f_name, node2.f_name)


# 168: DiscreteSubtypeName
@multimethod
def match_specific(node1: DiscreteSubtypeName, node2: DiscreteSubtypeName) -> bool:
    return match(node1.f_subtype, node2.f_subtype)


# 169: DottedName
@multimethod
def match_specific(node1: DottedName, node2: DottedName) -> bool:
    return match(node1.f_prefix, node2.f_prefix) \
           and match(node1.f_suffix, node2.f_suffix)


# 170: EndName
@multimethod
def match_specific(node1: EndName, node2: EndName) -> bool:
    return match(node1.f_name, node2.f_name)


# 171: ExplicitDeref
@multimethod
def match_specific(node1: ExplicitDeref, node2: ExplicitDeref) -> bool:
    return match(node1.f_prefix, node2.f_prefix)


# 172: QualExpr
@multimethod
def match_specific(node1: QualExpr, node2: QualExpr) -> bool:
    return match(node1.f_prefix, node2.f_prefix) \
           and match(node1.f_suffix, node2.f_suffix)


# 173: ReduceAttributeRef
@multimethod
def match_specific(node1: ReduceAttributeRef, node2: ReduceAttributeRef) -> bool:
    return match(node1.f_prefix, node2.f_prefix) \
           and match(node1.f_attribute, node2.f_attribute) \
           and match(node1.f_args, node2.f_args)


# 174: CharLiteral
@multimethod
def match_specific(node1: CharLiteral, node2: CharLiteral) -> bool:
    return True


# 175: Identifier TODO: check if this is correct
@multimethod
def match_specific(node1: Identifier, node2: Identifier) -> bool:
    return True

# 176: OpAbs
# 177: OpAnd
# 178: OpAndThen
# 179: OpConcat
# 180: OpDiv
# 181: OpDoubleDot
# 182: OpEq
# 183: OpGt
# 184: OpGte
# 185: OpIn
# 186: OpLt
# 187: OpLte
# 188: OpMinus
# 189: OpMod
# 190: OpMult
# 191: OpNeq
# 192: OpNot
# 193: OpNotIn
# 194: OpOr
# 195: OpOrElse
# 196: OpPlus
# 197: OpPow
# 198: OpRem
# 199: OpXor
@multimethod
def match_specific(node1: Op, node2: Op) -> bool:
    return node1 == node2


# 200: StringLiteral
@multimethod
def match_specific(node1: StringLiteral, node2: StringLiteral) -> bool:
    return True


# 201: NullLiteral
@multimethod
def match_specific(node1: NullLiteral, node2: NullLiteral) -> bool:
    return True


# 202: IntLiteral
@multimethod
def match_specific(node1: IntLiteral, node2: IntLiteral) -> bool:
    return True


# 203: RealLiteral
@multimethod
def match_specific(node1: RealLiteral, node2: RealLiteral) -> bool:
    return True


# 204: SyntheticIdentifier
# 205: TargetName


# 206: UpdateAttributeRef
@multimethod
def match_specific(node1: UpdateAttributeRef, node2: UpdateAttributeRef) -> bool:
    return match(node1.f_prefix, node2.f_prefix) \
           and match(node1.f_attribute, node2.f_attribute) \
           and match(node1.f_values, node2.f_values)


# 207: ParenExpr
@multimethod
def match_specific(node1: ParenExpr, node2: ParenExpr) -> bool:
    return match(node1.f_expr, node2.f_expr)


# 208: QuantifiedExpr
@multimethod
def match_specific(node1: QuantifiedExpr, node2: QuantifiedExpr) -> bool:
    return match(node1.f_quantifier, node2.f_quantifier) \
           and match(node1.f_loop_spec, node2.f_loop_spec) \
           and match(node1.f_expr, node2.f_expr)


# 209: RaiseExpr
@multimethod
def match_specific(node1: RaiseExpr, node2: RaiseExpr) -> bool:
    return match(node1.f_exception_name, node2.f_exception_name) \
           and match(node1.f_error_message, node2.f_error_message)


# 210: UnOp
@multimethod
def match_specific(node1: UnOp, node2: UnOp) -> bool:
    return match(node1.f_op, node2.f_op) \
           and match(node1.f_expr, node2.f_expr)


# 211: HandledStmts
@multimethod
def match_specific(node1: HandledStmts, node2: HandledStmts) -> bool:
    return match(node1.f_stmts, node2.f_stmts) \
           and match(node1.f_exceptions, node2.f_exceptions)


# 212: InterfaceKindLimited
# 213: InterfaceKindProtected
# 214: InterfaceKindSynchronized
# 215: InterfaceKindTask

# 216: IterTypeIn
@multimethod
def match_specific(node1: IterTypeIn, node2: IterTypeIn) -> bool:
    return True


# 217: IterTypeOf
@multimethod
def match_specific(node1: IterTypeOf, node2: IterTypeOf) -> bool:
    return True


# 218: LibraryItem
@multimethod
def match_specific(node1: LibraryItem, node2: LibraryItem) -> bool:
    return match(node1.f_has_private, node2.f_has_private) \
           and match(node1.f_item, node2.f_item)


# 219: LimitedAbsent
# 220: LimitedPresent


# 221: ForLoopSpec
@multimethod
def match_specific(node1: ForLoopSpec, node2: ForLoopSpec) -> bool:
    return match(node1.f_var_decl, node2.f_var_decl) \
           and match(node1.f_loop_type, node2.f_loop_type) \
           and match(node1.f_has_reverse, node2.f_has_reverse) \
           and match(node1.f_iter_expr, node2.f_iter_expr) \
           and match(node1.f_iter_filter, node2.f_iter_filter)


# 222: WhileLoopSpec
@multimethod
def match_specific(node1: WhileLoopSpec, node2: WhileLoopSpec) -> bool:
    return match(node1.f_expr, node2.f_expr)


# 223: ModeDefault
# 224: ModeIn
# 225: ModeInOut
# 226: ModeOut
@multimethod
def match_specific(node1: Mode, node2: Mode) -> bool:
    return True


# 227: MultiAbstractStateDecl
@multimethod
def match_specific(node1: MultiAbstractStateDecl, node2: MultiAbstractStateDecl) -> bool:
    return match(node1.f_decls, node2.f_decls)


# 228: NotNullAbsent TODO: check if this is correct
@multimethod
def match_specific(node1: NotNullAbsent, node2: NotNullAbsent) -> bool:
    return True


# 229: NotNullPresent TODO: check if this is correct
@multimethod
def match_specific(node1: NotNullPresent, node2: NotNullPresent) -> bool:
    return True


# 230: NullComponentDecl TODO: check if this is correct
@multimethod
def match_specific(node1: NullComponentDecl, node2: NullComponentDecl) -> bool:
    return True


# 231: OthersDesignator TODO: check if this is correct
@multimethod
def match_specific(node1: OthersDesignator, node2: OthersDesignator) -> bool:
    return True


# 232: OverridingNotOverriding TODO: check if this is correct
@multimethod
def match_specific(node1: OverridingNotOverriding, node2: OverridingNotOverriding) -> bool:
    return True


# 233: OverridingOverriding
@multimethod
def match_specific(node1: OverridingOverriding, node2: OverridingOverriding) -> bool:
    return True


# 234: OverridingUnspecified
@multimethod
def match_specific(node1: OverridingUnspecified, node2: OverridingUnspecified) -> bool:
    return True


# 235: Params
@multimethod
def match_specific(node1: Params, node2: Params) -> bool:
    return match(node1.f_params, node2.f_params)


# 236: ParenAbstractStateDecl
@multimethod
def match_specific(node1: ParenAbstractStateDecl, node2: ParenAbstractStateDecl) -> bool:
    return match(node1.f_decl, node2.f_decl)


# 237: PpElseDirective


# 238: PpElsifDirective
@multimethod
def match_specific(node1: PpElsifDirective, node2: PpElsifDirective) -> bool:
    return match(node1.f_expr, node2.f_expr) \
           and match(node1.f_then_kw, node2.f_then_kw)


# 239: PpEndIfDirective


# 240: PpIfDirective
@multimethod
def match_specific(node1: PpIfDirective, node2: PpIfDirective) -> bool:
    return match(node1.f_expr, node2.f_expr) \
           and match(node1.f_then_kw, node2.f_then_kw)


# 241: PpThenKw


# 242: PragmaNode
@multimethod
def match_specific(node1: PragmaNode, node2: PragmaNode) -> bool:
    return match(node1.f_id, node2.f_id) \
           and match(node1.f_args, node2.f_args)


# 243: PrivateAbsent TODO: double check, not present in Rejuvenation?
@multimethod
def match_specific(node1: PrivateAbsent, node2: PrivateAbsent) -> bool:
    return True


# 244: PrivatePresent TODO: double check, not present in Rejuvenation?
@multimethod
def match_specific(node1: PrivatePresent, node2: PrivatePresent) -> bool:
    return True


# 245: ProtectedDef
@multimethod
def match_specific(node1: ProtectedDef, node2: ProtectedDef) -> bool:
    return match(node1.f_public_part, node2.f_public_part) \
           and match(node1.f_private_part, node2.f_private_part) \
           and match(node1.f_end_name, node2.f_end_name)


# 246: ProtectedAbsent
# 247: ProtectedPresent
# 248: QuantifierAll
# 249: QuantifierSome


# 250: RangeSpec
@multimethod
def match_specific(node1: RangeSpec, node2: RangeSpec) -> bool:
    return match(node1.f_range, node2.f_range)


# 251: RenamingClause
@multimethod
def match_specific(node1: RenamingClause, node2: RenamingClause) -> bool:
    return match(node1.f_renamed_object, node2.f_renamed_object)


# 252: SyntheticRenamingClause
@multimethod
def match_specific(node1: SyntheticRenamingClause, node2: SyntheticRenamingClause) -> bool:
    return match(node1.f_renamed_object, node2.f_renamed_object)


# 253: ReverseAbsent
@multimethod
def match_specific(node1: ReverseAbsent, node2: ReverseAbsent) -> bool:
    return True


# 254: ReversePresent
@multimethod
def match_specific(node1: ReversePresent, node2: ReversePresent) -> bool:
    return True


# 255: SelectWhenPart
@multimethod
def match_specific(node1: SelectWhenPart, node2: SelectWhenPart) -> bool:
    return match(node1.f_cond_expr, node2.f_cond_expr) \
           and match(node1.f_stmts, node2.f_stmts)


# 256: AcceptStmt
@multimethod
def match_specific(node1: AcceptStmt, node2: AcceptStmt) -> bool:
    return match(node1.f_name, node2.f_name) \
           and match(node1.f_entry_index_expr, node2.f_entry_index_expr) \
           and match(node1.f_params, node2.f_params)


# 257: AcceptStmtWithStmts
@multimethod
def match_specific(node1: AcceptStmtWithStmts, node2: AcceptStmtWithStmts) -> bool:
    return match(node1.f_name, node2.f_name) \
           and match(node1.f_entry_index_expr, node2.f_entry_index_expr) \
           and match(node1.f_params, node2.f_params) \
           and match(node1.f_stmts, node2.f_stmts) \
           and match(node1.f_end_name, node2.f_end_name)


# 258: ForLoopStmt
@multimethod
def match_specific(node1: ForLoopStmt, node2: ForLoopStmt) -> bool:
    return match(node1.f_spec, node2.f_spec) \
           and match(node1.f_stmts, node2.f_stmts) \
           and match(node1.f_end_name, node2.f_end_name)


# 259: LoopStmt
@multimethod
def match_specific(node1: LoopStmt, node2: LoopStmt) -> bool:
    return match(node1.f_spec, node2.f_spec) \
           and match(node1.f_stmts, node2.f_stmts) \
           and match(node1.f_end_name, node2.f_end_name)


# 260: WhileLoopStmt
@multimethod
def match_specific(node1: WhileLoopStmt, node2: WhileLoopStmt) -> bool:
    return match(node1.f_spec, node2.f_spec) \
           and match(node1.f_stmts, node2.f_stmts) \
           and match(node1.f_end_name, node2.f_end_name)


# 261: BeginBlock
@multimethod
def match_specific(node1: BeginBlock, node2: BeginBlock) -> bool:
    return match(node1.f_stmts, node2.f_stmts) \
           and match(node1.f_end_name, node2.f_end_name)


# 262: DeclBlock
@multimethod
def match_specific(node1: DeclBlock, node2: DeclBlock) -> bool:
    return match(node1.f_decls, node2.f_decls) \
           and match(node1.f_stmts, node2.f_stmts) \
           and match(node1.f_end_name, node2.f_end_name)


# 263: CaseStmt
@multimethod
def match_specific(node1: CaseStmt, node2: CaseStmt) -> bool:
    return match(node1.f_expr, node2.f_expr) \
           and match(node1.f_pragmas, node2.f_pragmas) \
           and match(node1.f_alternatives, node2.f_alternatives)


# 264: ExtendedReturnStmt
@multimethod
def match_specific(node1: ExtendedReturnStmt, node2: ExtendedReturnStmt) -> bool:
    return match(node1.f_decl, node2.f_decl) \
           and match(node1.f_stmts, node2.f_stmts)


# 265: IfStmt
@multimethod
def match_specific(node1: IfStmt, node2: IfStmt) -> bool:
    return match(node1.f_cond_expr, node2.f_cond_expr) \
           and match(node1.f_then_stmts, node2.f_then_stmts) \
           and match(node1.f_alternatives, node2.f_alternatives) \
           and match(node1.f_else_stmts, node2.f_else_stmts)


# 266: NamedStmt
@multimethod
def match_specific(node1: NamedStmt, node2: NamedStmt) -> bool:
    return match(node1.f_decl, node2.f_decl) \
           and match(node1.f_stmt, node2.f_stmt)


# 267: SelectStmt
@multimethod
def match_specific(node1: SelectStmt, node2: SelectStmt) -> bool:
    return match(node1.f_guards, node2.f_guards) \
           and match(node1.f_else_stmts, node2.f_else_stmts) \
           and match(node1.f_abort_stmts, node2.f_abort_stmts)


# 268: ErrorStmt


# 269: AbortStmt
@multimethod
def match_specific(node1: AbortStmt, node2: AbortStmt) -> bool:
    return match(node1.f_names, node2.f_names)


# 270: AssignStmt
@multimethod
def match_specific(node1: AssignStmt, node2: AssignStmt) -> bool:
    return match(node1.f_dest, node2.f_dest) \
           and match(node1.f_expr, node2.f_expr)


# 271: CallStmt
@multimethod
def match_specific(node1: CallStmt, node2: CallStmt) -> bool:
    return match(node1.f_call, node2.f_call)


# 272: DelayStmt
@multimethod
def match_specific(node1: DelayStmt, node2: DelayStmt) -> bool:
    return match(node1.f_has_until, node2.f_has_until) \
           and match(node1.f_expr, node2.f_expr)


# 273: ExitStmt
@multimethod
def match_specific(node1: ExitStmt, node2: ExitStmt) -> bool:
    return match(node1.f_loop_name, node2.f_loop_name) \
           and match(node1.f_cond_expr, node2.f_cond_expr)


# 274: GotoStmt
@multimethod
def match_specific(node1: GotoStmt, node2: GotoStmt) -> bool:
    return match(node1.f_label_name, node2.f_label_name)


# 275: Label
@multimethod
def match_specific(node1: Label, node2: Label) -> bool:
    return match(node1.f_decl, node2.f_decl)


# 276: NullStmt TODO: check if this is correct
@multimethod
def match_specific(node1: NullStmt, node2: NullStmt) -> bool:
    return True


# 277: RaiseStmt
@multimethod
def match_specific(node1: RaiseStmt, node2: RaiseStmt) -> bool:
    return match(node1.f_exception_name, node2.f_exception_name) \
           and match(node1.f_error_message, node2.f_error_message)


# 278: RequeueStmt
@multimethod
def match_specific(node1: RequeueStmt, node2: RequeueStmt) -> bool:
    return match(node1.f_call_name, node2.f_call_name) \
           and match(node1.f_has_abort, node2.f_has_abort)


# 279: ReturnStmt
@multimethod
def match_specific(node1: ReturnStmt, node2: ReturnStmt) -> bool:
    return match(node1.f_return_expr, node2.f_return_expr)


# 280: TerminateAlternative
# 281: SubpKindFunction TODO: check if this is correct
@multimethod
def match_specific(node1: SubpKindFunction, node2: SubpKindFunction) -> bool:
    return True


# 282: SubpKindProcedure TODO: check if this is correct
@multimethod
def match_specific(node1: SubpKindProcedure, node2: SubpKindProcedure) -> bool:
    return True


# 283: Subunit
@multimethod
def match_specific(node1: Subunit, node2: Subunit) -> bool:
    return match(node1.f_name, node2.f_name) \
           and match(node1.f_body, node2.f_body)


# 284: SynchronizedAbsent
# 285: SynchronizedPresent
# 286: TaggedAbsent
# 287: TaggedPresent


# 288: TaskDef
@multimethod
def match_specific(node1: TaskDef, node2: TaskDef) -> bool:
    return match(node1.f_interfaces, node2.f_interfaces) \
           and match(node1.f_public_part, node2.f_public_part) \
           and match(node1.f_private_part, node2.f_private_part) \
           and match(node1.f_end_name, node2.f_end_name)


# 289: TypeAttributesRepository


# 290: AccessToSubpDef
@multimethod
def match_specific(node1: AccessToSubpDef, node2: AccessToSubpDef) -> bool:
    return match(node1.f_has_not_null, node2.f_has_not_null) \
           and match(node1.f_has_protected, node2.f_has_protected) \
           and match(node1.f_subp_spec, node2.f_subp_spec)


# 291: AnonymousTypeAccessDef
@multimethod
def match_specific(node1: AnonymousTypeAccessDef, node2: AnonymousTypeAccessDef) -> bool:
    return match(node1.f_has_not_null, node2.f_has_not_null) \
           and match(node1.f_type_decl, node2.f_type_decl)


# 292: TypeAccessDef
@multimethod
def match_specific(node1: TypeAccessDef, node2: TypeAccessDef) -> bool:
    return match(node1.f_has_not_null, node2.f_has_not_null) \
           and match(node1.f_has_all, node2.f_has_all) \
           and match(node1.f_has_constant, node2.f_has_constant) \
           and match(node1.f_subtype_indication, node2.f_subtype_indication)


# 293: ArrayTypeDef
@multimethod
def match_specific(node1: ArrayTypeDef, node2: ArrayTypeDef) -> bool:
    return match(node1.f_indices, node2.f_indices) \
           and match(node1.f_component_type, node2.f_component_type)


# 294: DerivedTypeDef
@multimethod
def match_specific(node1: DerivedTypeDef, node2: DerivedTypeDef) -> bool:
    return match(node1.f_has_abstract, node2.f_has_abstract) \
           and match(node1.f_has_limited, node2.f_has_limited) \
           and match(node1.f_has_synchronized, node2.f_has_synchronized) \
           and match(node1.f_subtype_indication, node2.f_subtype_indication) \
           and match(node1.f_interfaces, node2.f_interfaces) \
           and match(node1.f_record_extension, node2.f_record_extension) \
           and match(node1.f_has_with_private, node2.f_has_with_private)


# 295: EnumTypeDef
@multimethod
def match_specific(node1: EnumTypeDef, node2: EnumTypeDef) -> bool:
    return match(node1.f_enum_literals, node2.f_enum_literals)


# 296: FormalDiscreteTypeDef


# 297: InterfaceTypeDef
@multimethod
def match_specific(node1: InterfaceTypeDef, node2: InterfaceTypeDef) -> bool:
    return match(node1.f_interface_kind, node2.f_interface_kind) \
           and match(node1.f_interfaces, node2.f_interfaces)


# 298: ModIntTypeDef
@multimethod
def match_specific(node1: ModIntTypeDef, node2: ModIntTypeDef) -> bool:
    return match(node1.f_expr, node2.f_expr)


# 299: PrivateTypeDef
@multimethod
def match_specific(node1: PrivateTypeDef, node2: PrivateTypeDef) -> bool:
    return match(node1.f_has_abstract, node2.f_has_abstract) \
           and match(node1.f_has_tagged, node2.f_has_tagged) \
           and match(node1.f_has_limited, node2.f_has_limited)


# 300: DecimalFixedPointDef
@multimethod
def match_specific(node1: DecimalFixedPointDef, node2: DecimalFixedPointDef) -> bool:
    return match(node1.f_delta, node2.f_delta) \
           and match(node1.f_digits, node2.f_digits) \
           and match(node1.f_range, node2.f_range)


# 301: FloatingPointDef
@multimethod
def match_specific(node1: FloatingPointDef, node2: FloatingPointDef) -> bool:
    return match(node1.f_num_digits, node2.f_num_digits) \
           and match(node1.f_range, node2.f_range)


# 302: OrdinaryFixedPointDef
@multimethod
def match_specific(node1: OrdinaryFixedPointDef, node2: OrdinaryFixedPointDef) -> bool:
    return match(node1.f_delta, node2.f_delta) \
           and match(node1.f_range, node2.f_range)


# 303: RecordTypeDef
@multimethod
def match_specific(node1: RecordTypeDef, node2: RecordTypeDef) -> bool:
    return match(node1.f_has_abstract, node2.f_has_abstract) \
           and match(node1.f_has_tagged, node2.f_has_tagged) \
           and match(node1.f_has_limited, node2.f_has_limited) \
           and match(node1.f_record_def, node2.f_record_def)


# 304: SignedIntTypeDef
@multimethod
def match_specific(node1: SignedIntTypeDef, node2: SignedIntTypeDef) -> bool:
    return match(node1.f_range, node2.f_range)


# 305: AnonymousType
@multimethod
def match_specific(node1: AnonymousType, node2: AnonymousType) -> bool:
    return match(node1.f_type_decl, node2.f_type_decl)


# 306: EnumLitSynthTypeExpr


# 307: SubtypeIndication
@multimethod
def match_specific(node1: SubtypeIndication, node2: SubtypeIndication) -> bool:
    return match(node1.f_has_not_null, node2.f_has_not_null) \
           and match(node1.f_name, node2.f_name) \
           and match(node1.f_constraint, node2.f_constraint)


# 308: ConstrainedSubtypeIndication
@multimethod
def match_specific(node1: ConstrainedSubtypeIndication, node2: ConstrainedSubtypeIndication) -> bool:
    return match(node1.f_has_not_null, node2.f_has_not_null) \
           and match(node1.f_name, node2.f_name) \
           and match(node1.f_constraint, node2.f_constraint)


# 309: DiscreteSubtypeIndication
@multimethod
def match_specific(node1: DiscreteSubtypeIndication, node2: DiscreteSubtypeIndication) -> bool:
    return match(node1.f_has_not_null, node2.f_has_not_null) \
           and match(node1.f_name, node2.f_name) \
           and match(node1.f_constraint, node2.f_constraint)


# 310: SyntheticTypeExpr
@multimethod
def match_specific(node1: SyntheticTypeExpr, node2: SyntheticTypeExpr) -> bool:
    return match(node1.f_target_type, node2.f_target_type)


# 311: UnconstrainedArrayIndex
@multimethod
def match_specific(node1: UnconstrainedArrayIndex, node2: UnconstrainedArrayIndex) -> bool:
    return match(node1.f_subtype_indication, node2.f_subtype_indication)


# 312: UntilAbsent
# 313: UntilPresent


# 314: UsePackageClause
@multimethod
def match_specific(node1: UsePackageClause, node2: UsePackageClause) -> bool:
    return match(node1.f_packages, node2.f_packages)


# 315: UseTypeClause
@multimethod
def match_specific(node1: UseTypeClause, node2: UseTypeClause) -> bool:
    return match(node1.f_has_all, node2.f_has_all) \
           and match(node1.f_types, node2.f_types)


# 316: ValueSequence
@multimethod
def match_specific(node1: ValueSequence, node2: ValueSequence) -> bool:
    return match(node1.f_iter_assoc, node2.f_iter_assoc)


# 317: Variant
@multimethod
def match_specific(node1: Variant, node2: Variant) -> bool:
    return match(node1.f_choices, node2.f_choices) \
           and match(node1.f_components, node2.f_components)


# 318: VariantPart
@multimethod
def match_specific(node1: VariantPart, node2: VariantPart) -> bool:
    return match(node1.f_discr_name, node2.f_discr_name) \
           and match(node1.f_variant, node2.f_variant)


# 319: WithClause
@multimethod
def match_specific(node1: WithClause, node2: WithClause) -> bool:
    return match(node1.f_has_limited, node2.f_has_limited) \
           and match(node1.f_has_private, node2.f_has_private) \
           and match(node1.f_packages, node2.f_packages)

# 320: WithPrivateAbsent
# 321: WithPrivatePresent
