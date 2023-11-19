from abc import ABC, abstractmethod
from typing import Set


class TreeClassifier(ABC):
    """
    An interface to partition the nodes of an AST into sets of updated, deleted, moved,
    and updated nodes.
    """

    @abstractmethod
    def get_updated_srcs(self) -> Set[Tree]:
        """
        Return the set of updated nodes in the source AST.
        """
        pass

    @abstractmethod
    def get_deleted_srcs(self) -> Set[Tree]:
        """
        Return the set of deleted nodes in the source AST.
        """
        pass

    @abstractmethod
    def get_moved_srcs(self) -> Set[Tree]:
        """
        Return the set of moved nodes in the source AST.
        """
        pass

    @abstractmethod
    def get_updated_dsts(self) -> Set[Tree]:
        """
        Return the set of updated nodes in the destination AST.
        """
        pass

    @abstractmethod
    def get_inserted_dsts(self) -> Set[Tree]:
        """
        Return the set of inserted nodes in the destination AST.
        """
        pass

    @abstractmethod
    def get_moved_dsts(self) -> Set[Tree]:
        """
        Return the set of moved nodes in the destination AST.
        """
        pass
