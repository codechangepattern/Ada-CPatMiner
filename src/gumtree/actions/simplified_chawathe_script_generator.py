from gumtree.actions.chawathe_script_generator import ChawatheScriptGenerator
from gumtree.actions.edit_script_generator import EditScriptGenerator
from gumtree.actions.model.delete import Delete
from gumtree.actions.model.insert import Insert
from gumtree.actions.model.tree_delete import TreeDelete
from gumtree.actions.model.tree_insert import TreeInsert


class SimplifiedChawatheScriptGenerator(EditScriptGenerator):

    def compute_actions(self, ms):
        actions = ChawatheScriptGenerator().compute_actions(ms)
        return self.simplify(actions)

    @staticmethod
    def simplify(actions):
        added_trees = {}
        deleted_trees = {}

        for a in actions:
            if isinstance(a, Insert):
                added_trees[a.node] = a
            elif isinstance(a, Delete):
                deleted_trees[a.node] = a

        for t in added_trees.keys():
            if t.parent in added_trees and all(descendant in added_trees for descendant in t.get_descendants()):
                actions.remove(added_trees[t])
            else:
                if len(t.children) > 0 and all(descendant in added_trees for descendant in t.get_descendants()):
                    original_action = added_trees[t]
                    ti = TreeInsert(original_action.node, original_action.parent, original_action.position)
                    index = actions.last_index_of(original_action)
                    actions.add(ti, index)
                    actions.remove(index + 1)

        for t in deleted_trees.keys():
            if t.parent in deleted_trees and all(descendant in deleted_trees for descendant in t.get_descendants()):
                actions.remove(deleted_trees[t])
            else:
                if len(t.children) > 0 and all(descendant in deleted_trees for descendant in t.get_descendants()):
                    original_action = deleted_trees[t]
                    ti = TreeDelete(original_action.node)
                    index = actions.last_index_of(original_action)
                    actions.add(ti, index)
                    actions.remove(index + 1)

        return actions
