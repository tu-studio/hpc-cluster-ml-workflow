import os
import copy
import torch
from typing import Dict, Any, Generator, Tuple
from ruamel.yaml import YAML
from collections.abc import MutableMapping

def get_env_variable(var_name: str) -> str:
    value = os.getenv(var_name)
    if var_name == "SLURM_JOB_ID" and value is None:
        return None  
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
    

def prepare_device(request: str) -> torch.device:
    if request == "mps":
        if torch.backends.mps.is_available():
            device = torch.device("mps")
            print("Using MPS device")
        else:
            device = torch.device("cpu")
            print("MPS requested but not available. Using CPU device")
    elif request == "cuda":
        if torch.cuda.is_available():
            device = torch.device("cuda")
            print("Using CUDA device")
        else:
            device = torch.device("cpu")
            print("CUDA requested but not available. Using CPU device")
    else:
        device = torch.device("cpu")
        print("Using CPU device")
    return device


def set_random_seeds(random_seed):
    if 'random' in globals():
        random.seed(random_seed)
    else:
        print("The 'random' package is not imported, skipping random seed.")

    if 'np' in globals():
        np.random.seed(random_seed)
    else:
        print("The 'numpy' package is not imported, skipping numpy seed.")

    if 'torch' in globals():
        torch.manual_seed(random_seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(random_seed)
        if torch.backends.mps.is_available():
            torch.mps.manual_seed(random_seed)
    else:
        print("The 'torch' package is not imported, skipping torch seed.")
    if 'scipy' in globals():
        scipy.random.seed(random_seed)
    else:
        print("The 'scipy' package is not imported, skipping scipy seed.")