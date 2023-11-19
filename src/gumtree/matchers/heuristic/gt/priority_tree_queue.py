from abc import ABC, abstractmethod
from typing import Callable, List


class PriorityTreeQueue(ABC):

    @staticmethod
    def height_priority_calculator(t) -> int:
        return t.get_metrics().height

    @staticmethod
    def size_priority_calculator(t) -> int:
        return t.get_metrics().size

    @staticmethod
    def get_priority_calculator(name: str) -> Callable:
        if name == "size":
            return PriorityTreeQueue.size_priority_calculator
        elif name == "height":
            return PriorityTreeQueue.height_priority_calculator
        else:
            return PriorityTreeQueue.height_priority_calculator

    @abstractmethod
    def pop_open(self) -> List:
        pass

    @abstractmethod
    def set_priority_calculator(self, calculator: Callable) -> None:
        pass

    @abstractmethod
    def pop(self) -> List:
        pass

    @abstractmethod
    def open(self, tree) -> None:
        pass

    @abstractmethod
    def current_priority(self) -> int:
        pass

    @abstractmethod
    def set_minimum_priority(self, priority: int) -> None:
        pass

    @abstractmethod
    def get_minimum_priority(self) -> int:
        pass

    @abstractmethod
    def is_empty(self) -> bool:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass

    @staticmethod
    def synchronize(q1, q2) -> bool:
        while not(q1.is_empty() or q2.is_empty()) and q1.current_priority() != q2.current_priority():
            if q1.current_priority() > q2.current_priority():
                q1.pop_open()
            else:
                q2.pop_open()

        if q1.is_empty() or q2.is_empty():
            q1.clear()
            q2.clear()
            return False
        else:
            return True
