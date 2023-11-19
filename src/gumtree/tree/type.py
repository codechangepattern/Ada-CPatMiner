class Type:
    """
    Class representing the types of AST nodes. The types should be immutable and having
    a unique reference. There is one unique type (the empty type) that indicates that
    a given AST element does not have a type.
    """

    NO_TYPE = None  # Placeholder for the empty type

    def __init__(self, name: str):
        """
        :param name: The type name (immutable).
        """
        self.name = name

    @staticmethod
    def get_no_type():
        """Retrieve the empty type."""
        if Type.NO_TYPE is None:
            Type.NO_TYPE = TypeSet.type("")
        return Type.NO_TYPE

    def is_empty(self) -> bool:
        """
        Indicates whether or not the current type is the empty type.
        """
        return self == Type.get_no_type()

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)


class TypeFactory:
    def make_type(self, name: str) -> Type:
        """Factory method to create a new Type instance."""
        return Type(name)


class TypeSet:
    """
    Class dedicated to construct AST types.
    """

    class _TypeFactoryImplementation:
        """
        Inner static class that handles type creation and caching.
        """

        def __init__(self):
            self.types = {}

        def make_or_get_type(self, name):
            """
            Retrieve a type by name from the cache or create it if it doesn't exist.
            """
            if name is None:
                name = ""

            if name not in self.types:
                self.types[name] = Type(name)

            return self.types[name]

    # Singleton instance of the TypeFactoryImplementation
    _implementation = _TypeFactoryImplementation()

    @staticmethod
    def type(name):
        """
        Public method to get or create a type.
        """
        return TypeSet._implementation.make_or_get_type(name)
