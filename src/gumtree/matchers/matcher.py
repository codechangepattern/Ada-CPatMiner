from abc import ABC, abstractmethod


class Matcher(ABC):
    @abstractmethod
    def match(self, src, dst, mappings):
        pass
