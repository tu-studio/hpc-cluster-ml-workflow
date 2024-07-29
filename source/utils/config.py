import os
import copy
from typing import Dict, Any, Generator, Tuple
from ruamel.yaml import YAML
from collections.abc import MutableMapping


def get_env_variable(var_name: str) -> str:
    value = os.getenv(var_name)
    if value is None:
        raise EnvironmentError(f"The environment variable '{var_name}' is required but not set.")
    return value
    
class Params(dict):
    def __init__(self, yaml_file: str = 'params.yaml'):
        params: Dict[str, Any] = Params._load_params_from_yaml(yaml_file)
        super().__init__(params)

    @staticmethod
    def _load_params_from_yaml(yaml_file: str) -> Dict[str, Any]:
        yaml = YAML(typ='safe')
        with open(yaml_file, 'r') as file:
            params = yaml.load(file)
        return params

    @staticmethod
    def _flatten_dict_gen(d: MutableMapping[str, Any], parent_key: str, sep: str) -> Generator[Tuple[str, Any], None, None]:
        for k, v in d.items():
            new_key = parent_key + sep + k if parent_key else k
            if isinstance(v, MutableMapping):
                yield from Params._flatten_dict_gen(v, new_key, sep=sep)
            else:
                yield new_key, v

    @staticmethod
    def _flatten_dict(d: MutableMapping[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        return dict(Params._flatten_dict_gen(d, parent_key, sep))

    def flattened_copy(self) -> Dict[str, Any]:
        params_dict: Dict[str, Any] = copy.deepcopy(self)
        return self._flatten_dict(params_dict)