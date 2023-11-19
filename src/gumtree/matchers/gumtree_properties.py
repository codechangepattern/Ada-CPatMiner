class GumtreeProperties:
    def __init__(self):
        self.properties = {}

    def put(self, option, value):
        if option is not None:
            self.properties[option.name] = value

    def get(self, option):
        if option is not None:
            return self.properties.get(option.name)
        else:
            return None

    def set_if_not_present(self, property_name, value):
        return self.properties.setdefault(property_name, value)

    def try_configure(self, property_name, value):
        property = self.set_if_not_present(property_name, value)
        if property is not None:
            return str(property)
        return value

    def try_configure_int(self, property_name, value):
        property = self.set_if_not_present(property_name, value)
        if property is not None:
            try:
                return int(property)
            except ValueError:
                raise ValueError("Error parsing property as int")
        return value

    def try_configure_float(self, property_name, value):
        property = self.set_if_not_present(property_name, value)
        if property is not None:
            try:
                return float(property)
            except ValueError:
                raise ValueError("Error parsing property as float")
        return value

    def __str__(self):
        return ", ".join(f"{k}={v}" for k, v in self.properties.items())
