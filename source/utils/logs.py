# Copyright 2024 tu-studio
# This file is licensed under the Apache License, Version 2.0.
# See the LICENSE file in the root of this project for details.


"""
This module handles the logging and summary writing for the project.
"""

import datetime
import os
import shutil
from pathlib import Path, PosixPath
from typing import Any, Dict, Optional, Union

from torch.utils.tensorboard import SummaryWriter
from torch.utils.tensorboard.summary import hparams

if __name__ == "__main__":
    import config
else:
    from utils import config

class CustomSummaryWriter(SummaryWriter):
    """
    A custom subclass of the TensorBoard SummaryWriter that allows for logging hyperparameters,
    displaying scalar metrics in the HParams tab, and automatically synchronizing logs with a remote directory.

    Args:
        log_dir (Union[str, PosixPath]): Directory where the TensorBoard logs will be stored.
        params (Optional[config.Params[str, Any]]): config.Params object of DVC hyperparameters to display. Defaults to None.
        metrics (Optional[Dict[str, None]]): Dictionary of initial metrics to display in the HParams tab. Defaults to {}.
        sync_interval (Optional[int]): Number of steps between automatic syncs to the remote directory.
                                       Defaults to the value of the 'TUSTU_SYNC_INTERVAL' environment variable.
                                       If set to 0, no automatic syncs will be performed.
        remote_dir (Optional[Union[str, PosixPath]]): Remote directory with format 'host:dir' to which logs are synced.
                                Defaults to None, in which case the remote directory is constructed from environment variables.
    """

    def __init__(
        self,
        log_dir: Union[str, PosixPath],
        params: Optional[config.Params[str, Any]] = None,
        metrics: Optional[Dict[str, None]] = {},
        sync_interval: Optional[int] = None,
        remote_dir: Optional[Union[str, PosixPath]] = None,
    ):
        super().__init__(log_dir=log_dir)

        self.sync_interval = (
            sync_interval
            if sync_interval is not None
            else int(config.get_env_variable("TUSTU_SYNC_INTERVAL"))
        )
        self.remote_dir = (
            remote_dir or self._construct_remote_dir()
            if self.sync_interval != 0
            else None
        )
        self.datetime = self._extract_datetime_from_log_dir(log_dir)

        if params:
            self._log_hyperparameters(params, metrics, log_dir)

        self.current_step = 0

    def _construct_remote_dir(self) -> str:
        """Constructs the remote directory path based on environment variables."""
        tensorboard_host_dir = config.get_env_variable("TUSTU_TENSORBOARD_HOST_DIR")
        tensorboard_host = config.get_env_variable("TUSTU_TENSORBOARD_HOST")
        tensorboard_host_savepath = Path(
            f'{tensorboard_host_dir}/{config.get_env_variable("TUSTU_PROJECT_NAME")}/logs/tensorboard'
        )
        os.system(f"ssh {tensorboard_host} 'mkdir -p {tensorboard_host_savepath}'")
        return f"{tensorboard_host}:{tensorboard_host_savepath}"

    def _extract_datetime_from_log_dir(self, log_dir: Union[str, PosixPath]) -> str:
        """Extracts datetime information from the log directory path."""
        return str(log_dir).split("/")[-1].split("_")[0]

    def _log_hyperparameters(
        self,
        params: config.Params[str, Any],
        metrics: Dict[str, None],
        log_dir: str,
    ) -> None:
        """Logs hyperparameters and initial metrics to TensorBoard."""
        params = params.flattened_copy()
        params["datetime"] = self.datetime
        self._add_hparams(hparam_dict=params, metric_dict=metrics, run_name=log_dir)

    def step(self) -> None:
        """
        Increments the current step and triggers log synchronization if the sync interval is reached.
        """
        self.current_step += 1
        if self.sync_interval != 0:
            if self.current_step % self.sync_interval == 0:
                self.flush()
                self._sync_logs()

    def _sync_logs(self) -> None:
        """Synchronizes the logs with the remote directory."""
        # path = f'mkdir -p {self.remote_dir} && rsync'
        os.system(f"rsync -rv --inplace --progress {self.log_dir} {self.remote_dir}")

    def _add_hparams(
        self,
        hparam_dict: Dict[str, Any],
        metric_dict: Dict[str, Optional[float]],
        hparam_domain_discrete: Optional[Dict[str, list]] = None,
        run_name: Optional[str] = None,
    ) -> None:
        """
        Adds hyperparameters and metrics to the same TensorBoard log file and enables scalar metrics in the HParams tab.

        Args:
            hparam_dict (Dict[str, float]): Dictionary of hyperparameters.
            metric_dict (Dict[str, Optional[float]]): Dictionary of metrics.
            hparam_domain_discrete (Optional[Dict[str, list]]): Discrete domains for hyperparameters.
            run_name (Optional[str]): Name of the run in TensorBoard.

        Raises:
            TypeError: If `hparam_dict` or `metric_dict` are not dictionaries.
        """
        if not isinstance(hparam_dict, dict) or not isinstance(metric_dict, dict):
            raise TypeError("hparam_dict and metric_dict should be dictionary.")

        exp, ssi, sei = hparams(hparam_dict, metric_dict, hparam_domain_discrete)

        self.file_writer.add_summary(exp)
        self.file_writer.add_summary(ssi)
        self.file_writer.add_summary(sei)
        for k, v in metric_dict.items():
            if v is not None:
                self.add_scalar(k, v)


def return_tensorboard_path() -> PosixPath:
    """
    Returns the path to the TensorBoard logs directory for the current experiment.
    The path is constructed using the default directory, current datetime, and DVC experiment name.

    Returns:
        PosixPath: The path to the TensorBoard logs directory.
    """
    default_dir = config.get_env_variable("DEFAULT_DIR")
    dvc_exp_name = config.get_env_variable("DVC_EXP_NAME")
    current_datetime = datetime.datetime.now().strftime("%Y%m%d-%H%M")

    tensorboard_path = Path(
        f"{default_dir}/logs/tensorboard/{current_datetime}_{dvc_exp_name}"
    )
    tensorboard_path.mkdir(parents=True, exist_ok=True)

    return tensorboard_path


def copy_tensorboard_logs() -> str:
    """
    Copies the TensorBoard logs specific to the current experiment from the host directory
    to the temporary experiment directory.

    Returns:
        str: The name of the copied directory.
    """
    default_dir = config.get_env_variable("DEFAULT_DIR")
    dvc_exp_name = config.get_env_variable("DVC_EXP_NAME")

    tensorboard_logs_source = Path(f"{default_dir}/logs/tensorboard")
    tensorboard_logs_destination = Path(f"exp_logs/tensorboard")
    tensorboard_logs_destination.mkdir(parents=True, exist_ok=True)
    for f in tensorboard_logs_source.iterdir():
        if f.is_dir() and f.name.endswith(dvc_exp_name):
            dir_name = f.name
            shutil.copytree(
                f, tensorboard_logs_destination / f.name, dirs_exist_ok=True
            )
            print(
                f"TensorBoard log '{f.name}' copied to '{tensorboard_logs_destination / f.name}'"
            )
            return f.name
    print("No TensorBoard logs found. Skipping copying.")
    return f"no_tensorboard_logs_{dvc_exp_name}"


def copy_slurm_logs(dir_name) -> None:
    """
    Copies the SLURM logs specific to the current experiment from the host directory
    to the temporary experiment directory.

    If the SLURM_JOB_ID is not found, the copying process is skipped.

    Args:
        dir_name (str): The name of the directory to copy the SLURM logs to.

    Raises:
        ValueError: If the directory name does not end with the DVC experiment name.
    """
    default_dir = config.get_env_variable("DEFAULT_DIR")
    current_slurm_job_id = config.get_env_variable("SLURM_JOB_ID")
    dvc_exp_name = config.get_env_variable("DVC_EXP_NAME")

    if dir_name is None:
        raise ValueError("Directory name is None.")
    elif not dir_name.endswith(dvc_exp_name):
        raise ValueError(f"Directory '{dir_name}' does not end with '{dvc_exp_name}'")

    if current_slurm_job_id:
        slurm_logs_source = Path(f"{default_dir}/logs/slurm")
        slurm_logs_destination = Path(f"exp_logs/slurm/{dir_name}")
        slurm_logs_destination.mkdir(parents=True, exist_ok=True)
        if current_slurm_job_id is not None:
            for f in slurm_logs_source.iterdir():
                if f.is_file() and f.name.endswith(current_slurm_job_id + ".out"):
                    shutil.copy(f, slurm_logs_destination)
        print(f"SLURM log 'slurm-{current_slurm_job_id}.out' copied to {slurm_logs_destination / f.name}.")
    else:
        print("No SLURM_JOB_ID found. Skipping SLURM logs copying.")


def main():
    """Main function to copy SLURM and TensorBoard logs."""
    dir_name = copy_tensorboard_logs()
    copy_slurm_logs(dir_name=dir_name)


if __name__ == "__main__":
    main()
