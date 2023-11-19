from abc import ABC

from gumtree.matchers.configurable import Configurable
from gumtree.matchers.matcher import Matcher


class ConfigurableMatcher(Matcher, Configurable, ABC):
    pass
