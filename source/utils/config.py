import os
import copy
from typing import Dict, Any, Generator, Tuple
import dvc.api
from collections.abc import MutableMapping


class Environment:
    def __init__(self):
        self.tustu_logs_dir = self._get_env_variable('TUSTU_LOGS_DIR')
        self.default_dir = self._get_env_variable('DEFAULT_DIR')
        self.dvc_exp_name = self._get_env_variable('DVC_EXP_NAME')
        self.tustu_exp_logs_dir = self._get_env_variable('TUSTU_EXP_LOGS_DIR')

    @staticmethod
    def _get_env_variable(var_name: str) -> str:
        value = os.environ.get(var_name)
        if value is None:
            raise EnvironmentError(f"The environment variable '{var_name}' is not set.")
        return value
    
class Params(dict):
    def __init__(self, yaml_file: str = 'params.yaml'):
        params: Dict[str, Any] = dvc.api.params_show(yaml_file)
        super().__init__(params)

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

    def get_flat_copy(self) -> Dict[str, Any]:
        params_dict: Dict[str, Any] = copy.deepcopy(self)
        return self._flatten_dict(params_dict)

    
