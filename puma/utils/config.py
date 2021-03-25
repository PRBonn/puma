import os

import yaml
from easydict import EasyDict


def load_config_from_yaml(path):
    """Returns an EasyDict from the given path to a config.yml file.

    The path to the config file can be specified with an absolute
    path(e.g. ../../path_to_config/config.yml) or using a relative path
    to the current git directory(e.g config/config.yml). This function
    will try to load first from the absolute path and fallback to the
    git repo.
    """
    try:
        config_file = open(path)
    except FileNotFoundError:
        raise FileNotFoundError("{} file doesn't exist".format(path))

    # Returns any of the two possible config_file
    return EasyDict(yaml.safe_load(config_file))


def save_config_yaml(path, config):
    """Stores the given config dictionary to the specified path."""
    with open(path, "w") as outfile:
        yaml.dump(config, outfile, default_flow_style=False)
