from enum import Enum


class ConfigurationOptions(Enum):
    """
    Enum defining configuration options for different matchers
    """
    bu_minsim = 1
    bu_minsize = 2
    st_minprio = 3
    st_priocalc = 4
    cd_labsim = 5
    cd_maxleaves = 6
    cd_structsim1 = 7
    cd_structsim2 = 8
    xy_minsim = 9
