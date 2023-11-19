from abc import ABC, abstractmethod


class EditScriptGenerator(ABC):
    """
    Interface for script generators that compute edit scripts from mappings.
    """

    @abstractmethod
    def compute_actions(self, mappings):
        """
        Compute and return the edit script for the provided mappings.
        """
        pass
