# Copyright 2024 tu-studio
# This file is licensed under the Apache License, Version 2.0.
# See the LICENSE file in the root of this project for details.

"""
This module handles the configuration for the python project.
"""

import copy
import os
from collections.abc import MutableMapping
from typing import Any, Dict, Generator, Tuple

import torch
from ruamel.yaml import YAML


def get_env_variable(var_name: str) -> str:
    """
    Retrieves the value of a specified environment variable.

    Args:
        var_name (str): The name of the environment variable to retrieve.

    Returns:
        str: The value of the specified environment variable.

    Raises:
        EnvironmentError: If the environment variable is required but not set,
                          except for "SLURM_JOB_ID", where None is returned instead.

    Note:
        If the environment variable is "SLURM_JOB_ID" and it is not set, the function returns None.
        For all other environment variables, an EnvironmentError is raised if they are not set.
    """
    value = os.getenv(var_name)
    if var_name == "SLURM_JOB_ID" and value is None:
        return None
    if value is None:
        raise EnvironmentError(
            f"The environment variable {var_name} is required but not set."
        )
    return value


class Params(dict):
    """
    A dictionary subclass that loads parameters from a YAML file and provides additional
    functionality to flatten nested dictionaries.

    Args:
        yaml_file (str): The path to the YAML file containing the parameters. Defaults to 'params.yaml'.

    Attributes:
        None (The parameters are stored in the dictionary itself, accessible via standard dict methods).
    """

    def __init__(self, yaml_file: str = "params.yaml"):
        params: Dict[str, Any] = Params._load_params_from_yaml(yaml_file)
        super().__init__(params)

    @staticmethod
    def _load_params_from_yaml(yaml_file: str) -> Dict[str, Any]:
        """
        Initializes the Params object by loading parameters from the specified YAML file.

        Args:
            yaml_file (str): The path to the YAML file to load parameters from.
                Defaults to 'params.yaml'.
        """
        yaml = YAML(typ="safe")
        with open(yaml_file, "r") as file:
            params = yaml.load(file)
        return params

    @staticmethod
    def _flatten_dict_gen(
        d: MutableMapping[str, Any], parent_key: str, sep: str
    ) -> Generator[Tuple[str, Any], None, None]:
        """
        A generator that recursively flattens a nested dictionary.

        Args:
            d (MutableMapping[str, Any]): The dictionary to flatten.
            parent_key (str): The base key for the current level of the dictionary.
            sep (str): The separator to use between keys in the flattened dictionary.

        Yields:
            Generator[Tuple[str, Any], None, None]: Pairs of flattened keys and their corresponding values.
        """
        for k, v in d.items():
            new_key = parent_key + sep + k if parent_key else k
            if isinstance(v, MutableMapping):
                yield from Params._flatten_dict_gen(v, new_key, sep=sep)
            else:
                yield new_key, v

    @staticmethod
    def _flatten_dict(
        d: MutableMapping[str, Any], parent_key: str = "", sep: str = "."
    ) -> Dict[str, Any]:
        """
        Flattens a nested dictionary into a single level dictionary with concatenated keys.

        Args:
            d (MutableMapping[str, Any]): The dictionary to flatten.
            parent_key (str): The base key for the current level of the dictionary.
                Defaults to ''.
            sep (str): The separator to use between keys in the flattened dictionary.
                Defaults to '.'.

        Returns:
            Dict[str, Any]: A flattened dictionary where nested keys are concatenated by the separator.
        """
        return dict(Params._flatten_dict_gen(d, parent_key, sep))

    def flattened_copy(self) -> Dict[str, Any]:
        """
        Creates a flattened copy of the Params dictionary.

        Returns:
            Dict[str, Any]: A flattened dictionary where nested keys are concatenated by the separator.
        """
        params_dict: Dict[str, Any] = copy.deepcopy(self)
        return self._flatten_dict(params_dict)


def prepare_device(request: str) -> torch.device:
    """
    Prepares the appropriate PyTorch device based on the user's request.

    Args:
        request (str): The type of device requested. Options include "mps", "cuda", and "cpu".
                       - "mps": Metal Performance Shaders (for Apple Silicon GPUs).
                       - "cuda": NVIDIA CUDA GPU.
                       - "cpu": Central Processing Unit.

    Returns:
        torch.device: The device that will be used for tensor operations.

    Notes:
        - If "mps" is requested but not available, the function defaults to "cpu".
        - If "cuda" is requested but not available, the function defaults to "cpu".
        - If the request is neither "mps" nor "cuda", the function defaults to "cpu".

    Example:
        device = prepare_device("cuda")
    """
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


def set_random_seeds(random_seed: int) -> None:
    """
    Sets the random seed for various libraries to ensure reproducibility.

    Args:
        random_seed (int): The seed value to be used for random number generation.

    Notes:
        - Sets the seed for the following libraries if they are available:
          - `random`: Python's built-in random module.
          - `numpy`: NumPy for handling arrays and matrices.
          - `torch`: PyTorch for deep learning operations.
          - `scipy`: SciPy for scientific computing.
        - If a library is not imported in the global scope, the seed setting for that library will be skipped.

    Example:
        set_random_seeds(42)
    """
    if "random" in globals():
        random.seed(random_seed)  # type: ignore
    else:
        print("The 'random' package is not imported, skipping random seed.")

    if "np" in globals():
        np.random.seed(random_seed)  # type: ignore
    else:
        print("The 'numpy' package is not imported, skipping numpy seed.")

    if "torch" in globals():
        torch.manual_seed(random_seed)  # type: ignore
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(random_seed)
        if torch.backends.mps.is_available():
            torch.mps.manual_seed(random_seed)
    else:
        print("The 'torch' package is not imported, skipping torch seed.")
    if "scipy" in globals():
        scipy.random.seed(random_seed)  # type: ignore
    else:
        print("The 'scipy' package is not imported, skipping scipy seed.")
