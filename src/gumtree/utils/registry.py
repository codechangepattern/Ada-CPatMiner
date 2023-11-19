from abc import ABC, abstractmethod
from collections import defaultdict


class Registry(ABC):
    class Priority:
        MAXIMUM = 0
        HIGH = 25
        MEDIUM = 50
        LOW = 75
        MINIMUM = 100

    def __init__(self):
        self.entries = defaultdict(list)

    def get(self, key, *args):
        factory = self.get_factory(key)
        if factory is not None:
            return factory.instantiate(*args)
        return None

    def get_factory(self, key):
        entry = self.find(key)
        if entry is not None:
            return entry.factory
        return None

    @abstractmethod
    def find(self, key):
        pass

    def find_by_id(self, id):
        for e in self.entries.values():
            if e.id == id:
                return e
        return None

    def install(self, clazz, annotation):
        entry = self.new_entry(clazz, annotation)
        self.entries[entry.id].append(entry)

    def clear(self):
        self.entries.clear()

    @abstractmethod
    def new_entry(self, clazz, annotation):
        pass

    def find_entry(self, key):
        for e in self.entries.values():
            if e.handle(key):
                return e
        return None

    def find_by_class(self, aClass):
        for e in self.entries.values():
            if e.clazz == aClass:
                return e
        return None

    def get_entries(self):
        return self.entries

    class Entry:
        def __init__(self, id, clazz, factory, priority):
            self.id = id
            self.clazz = clazz
            self.factory = factory
            self.priority = priority

        @abstractmethod
        def handle(self, key):
            pass

        def __str__(self):
            return self.id

    class Factory:
        @abstractmethod
        def new_instance(self, *args):
            pass

        def instantiate(self, *args):
            try:
                return self.new_instance(*args)
            except Exception:
                return None
