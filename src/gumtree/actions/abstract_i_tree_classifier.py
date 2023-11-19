from abc import ABC, abstractmethod
from typing import Set


class AbstractITreeClassifier(ABC):

    def __init__(self, diff):
        self.diff = diff
        self.src_upd_trees = set()
        self.dst_upd_trees = set()
        self.src_mv_trees = set()
        self.dst_mv_trees = set()
        self.src_del_trees = set()
        self.dst_add_trees = set()
        self.classify()

    @abstractmethod
    def classify(self):
        pass

    def get_updated_srcs(self) -> Set:
        return self.src_upd_trees

    def get_updated_dsts(self) -> Set:
        return self.dst_upd_trees

    def get_moved_srcs(self) -> Set:
        return self.src_mv_trees

    def get_moved_dsts(self) -> Set:
        return self.dst_mv_trees

    def get_deleted_srcs(self) -> Set:
        return self.src_del_trees

    def get_inserted_dsts(self) -> Set:
        return self.dst_add_trees
