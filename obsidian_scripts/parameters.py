import yaml
import os

from obsidian_scripts.paths import LIB_DIR


# Load parameters from yaml file
def get_parameters():
    path = os.path.join(LIB_DIR, "resources/params.yml")
    with open(path) as f:
        params = yaml.load(f, Loader=yaml.FullLoader)
    return params
