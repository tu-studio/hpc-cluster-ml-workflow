from ruamel.yaml import YAML
from box import ConfigBox
import os

class EnvironmentConfig:
    def __init__(self):
        self.tustu_logs_path = self.get_env_variable('TUSTU_LOGS_PATH' 'logs')
        self.default_dir = self.get_env_variable('DEFAULT_DIR')
        self.experiment_name = self.get_env_variable('DVC_EXP_NAME', 'default_experiment')

    @staticmethod
    def get_env_variable(var_name, default_value=None):
        value = os.environ.get(var_name, default_value)
        if value is None:
            raise EnvironmentError(f"The environment variable '{var_name}' is not set.")
        return value

def load_params(param_file='params.yaml'):
    yaml = YAML(typ="safe")
    with open(param_file, 'r') as file:
        params = ConfigBox(yaml.load(file))
    return params

def flatten_dict(d, parent_key='', sep='.'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)