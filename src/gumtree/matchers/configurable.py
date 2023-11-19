from gumtree.matchers.gumtree_properties import GumtreeProperties


class Configurable:
    def configure(self, properties):
        """
        Default configure method that does nothing.
        Has to be overridden by subclasses to make use of the
        data inside of the provided GumTreeProperties object.
        """
        pass

    def get_applicable_options(self):
        """
        Return the list of options applicable to the objects.
        """
        return set()

    def set_option(self, option, value):
        """
        Modify the provided option to the provided value. Raise an exception
        if the provided option is not in the set of applicable options.
        """
        if option not in self.get_applicable_options():
            raise ValueError(
                "Option {} is not allowed. Applicable options are: {}".format(
                    option, self.get_applicable_options()))

        properties = GumtreeProperties()
        properties.put(option, value)
        self.configure(properties)
