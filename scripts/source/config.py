from ruamel.yaml import YAML
from box import ConfigBox

def load_params(param_file='params.yaml'):
    yaml = YAML(typ="safe")
    with open(param_file, 'r') as file:
        params = ConfigBox(yaml.load(file))
    return params