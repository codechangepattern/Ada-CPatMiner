import re

from gumtree.tree.default_tree import DefaultTree
from gumtree.tree.fake_tree import FakeTree


class TreeContext:
    def __init__(self):
        self.trees = {}
        self.metadata = {}
        self.serializers = MetadataSerializers()
        self.root = None
        self.src = None

    def __str__(self):
        # Assuming a function 'to_text' exists in some module 'tree_io_utils'
        # return tree_io_utils.to_text(self).to_string()
        # Placeholder implementation for this example
        return str(self.metadata)

    def set_root(self, root):
        self.root = root

    def set_source(self, source):
        self.src = source

    def set_trees(self, trees):
        self.trees = trees

    def get_root(self):
        return self.root

    def get_source(self):
        return self.src

    def get_trees(self):
        return self.trees

    def create_tree(self, type, label=None):
        return DefaultTree(type, label)

    def create_fake_tree(self, *trees):
        return FakeTree(trees)

    def get_metadata(self, key=None):
        if key:
            return self.metadata.get(key)
        return iter(self.metadata.items())

    def set_metadata(self, key, value):
        return self.metadata.setdefault(key, value)

    def get_serializers(self):
        return self.serializers

    # def export(self, *args):
    #     if isinstance(args[0], MetadataSerializers):
    #         self.serializers.add_all(args[0])
    #     elif isinstance(args[0], str) and isinstance(args[1], MetadataSerializer):
    #         self.serializers.add(args[0], args[1])
    #     elif isinstance(args[0], str):
    #         for n in args:
    #             self.serializers.add(n, lambda x: str(x))
    #     return self


class Marshallers:
    valid_id = re.compile(r"[a-zA-Z0-9_]*")

    def __init__(self):
        self.serializers = {}

    def add_all(self, other):
        if isinstance(other, Marshallers):
            self.add_all(other.serializers)
        else:
            for k, s in other.items():
                self.add(k, s)

    def add(self, name, serializer):
        if not self.valid_id.match(name):
            raise RuntimeError("Invalid key for serialization")
        self.serializers[name] = serializer

    def remove(self, key):
        self.serializers.pop(key, None)

    def exports(self):
        return set(self.serializers.keys())


class MetadataSerializers(Marshallers):
    def serialize(self, formatter, key, value):
        s = self.serializers.get(key)
        if s:
            # Assuming a method 'serialize_attribute' exists in formatter
            formatter.serialize_attribute(key, s(value))


class MetadataUnserializers(Marshallers):
    def load(self, tree, key, value):
        s = self.serializers.get(key)
        if s:
            if key == "pos":
                tree.set_pos(int(value))
            elif key == "length":
                tree.set_length(int(value))
            else:
                tree.set_metadata(key, s(value))
