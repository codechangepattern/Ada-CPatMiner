from abc import ABC, abstractmethod
from collections import defaultdict

from gumtree.utils.registry import Registry


class Matchers(Registry):
    registry = None

    @staticmethod
    def get_instance():
        if Matchers.registry is None:
            Matchers.registry = Matchers()
        return Matchers.registry

    def get_matcher(self, id):
        return self.get(id)

    def get_matcher_with_fallback(self, id):
        if id is None:
            return self.get_matcher()

        matcher = self.get(id)
        if matcher is not None:
            return matcher
        else:
            return self.get_matcher()

    def get_matcher(self):
        return self.default_matcher_factory.instantiate()

    def __init__(self):
        super().__init__()
        self.default_matcher_factory = None
        self.lowest_priority = None

    def install(self, clazz, annotation):
        if annotation is None:
            raise ValueError("Expecting @Register annotation on " + clazz.__name__)
        if self.default_matcher_factory is None:
            self.default_matcher_factory = self.default_factory(clazz)
            self.lowest_priority = annotation.priority
        elif annotation.priority < self.lowest_priority:
            self.default_matcher_factory = self.default_factory(clazz)
            self.lowest_priority = annotation.priority

        super().install(clazz, annotation)

    def clear(self):
        super().clear()
        self.default_matcher_factory = None

    def get_name(self, annotation, clazz):
        return annotation.id

    def new_entry(self, clazz, annotation):
        return self.Entry(annotation.id, clazz,
                          self.default_factory(clazz), annotation.priority)

    class Entry(Registry.Entry):
        def handle(self, key):
            return self.id == key
