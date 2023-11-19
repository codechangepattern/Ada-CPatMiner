from gumtree.actions.all_nodes_classifier import AllNodesClassifier
from gumtree.actions.simplified_chawathe_script_generator import SimplifiedChawatheScriptGenerator
from gumtree.matchers.composite_matchers import MATCHERS
from gumtree.matchers.gumtree_properties import GumtreeProperties
from gumtree.matchers.matchers import Matchers


class Diff:
    def __init__(self, src, dst, mappings, edit_script):
        self.src = src
        self.dst = dst
        self.mappings = mappings
        self.edit_script = edit_script

    @staticmethod
    def compute(src_root, src_source, dst_root, dst_source, tree_generator=None, matcher=None, properties=None):
        if not properties:
            properties = GumtreeProperties()

        src = tree_generator.generate(src_root, src_source)
        dst = tree_generator.generate(dst_root, dst_source)

        return Diff._compute(src, dst, matcher, properties)

    @staticmethod
    def _compute(src, dst, matcher, properties):
        m = MATCHERS['gumtree-simple']
        # m.configure(properties)
        mappings = m.match(src.get_root(), dst.get_root())
        edit_script = SimplifiedChawatheScriptGenerator().compute_actions(mappings)
        return Diff(src, dst, mappings, edit_script)

    def create_all_node_classifier(self):
        return AllNodesClassifier(self)

    def create_root_nodes_classifier(self):
        return OnlyRootsClassifier(self)
