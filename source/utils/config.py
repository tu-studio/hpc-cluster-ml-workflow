from ruamel.yaml import YAML
from box import ConfigBox

def load_params(param_file='params.yaml'):
    yaml = YAML(typ="safe")
    with open(param_file, 'r') as file:
        params = ConfigBox(yaml.load(file))
    return params

def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)