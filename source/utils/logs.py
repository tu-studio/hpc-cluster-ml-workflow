import shutil
from pathlib import Path
import torch
from torch.utils.tensorboard import SummaryWriter
from torch.utils.tensorboard.summary import hparams
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))
from utils import config
import os
import datetime
import subprocess
class CustomSummaryWriter(SummaryWriter):
    """
    A custom subclass of the TensorBoard SummaryWriter that allows for logging hyperparameters to the same log file, display scalar metrics in the HParams tab,
    and automatically synchronizing logs with a remote directory at regular intervals.

    Args:
        log_dir (str): Directory where the TensorBoard logs will be stored.
        params (Params, optional): Params object of DVC hyperparameters to log. Defaults to None.
        metrics (dict, optional): Dictionary of initial metrics to log. Defaults to an empty dictionary.
        sync_interval (int, optional): Number of steps between automatic syncs to the remote directory. 
                                       Defaults to the value of the 'TUSTU_SYNC_INTERVAL' environment variable.
                                       If set to 0, no automatic syncs will be performed. 
        remote_dir (str, optional): Remote directory to which logs are synced. 
                                    Defaults to a path constructed from environment variables.
    """    
    def __init__(self, log_dir, params=None, metrics={}, sync_interval=None, remote_dir=None): 
        super().__init__(log_dir=log_dir)
        if sync_interval is None:
            sync_interval = int(config.get_env_variable('TUSTU_SYNC_INTERVAL')) 
        if remote_dir is None and sync_interval != 0:
            self.tensorboard_host_dir = config.get_env_variable('TUSTU_TENSORBOARD_HOST_DIR')
            self.tensorboard_host = config.get_env_variable('TUSTU_TENSORBOARD_HOST')
            self.tensorboard_host_savepath = Path(f'{self.tensorboard_host_dir}/{config.get_env_variable("TUSTU_PROJECT_NAME")}/logs/tensorboard')  
            remote_dir = f'{self.tensorboard_host}:{self.tensorboard_host_savepath}'
        self.datetime = str(log_dir).split('/')[-1].split('_')[0]
        if params is not None:
            params = params.flattened_copy()
            params['datetime'] = self.datetime
            self._add_hparams(hparam_dict=params, metric_dict=metrics, run_name=log_dir)
        self.sync_interval = sync_interval
        self.remote_dir = remote_dir
        self.current_step = 0

    def step(self) -> None:
        """
        Increments the current step and calls sync_logs() if the sync interval is reached.
        """
        self.current_step += 1
        if self.sync_interval != 0:
            if self.current_step % self.sync_interval == 0:
                self.flush()
                self._sync_logs()

    def _sync_logs(self) -> None:
        """
        Synchronizes the logs with the remote directory.
        """
        # path = f'mkdir -p {self.remote_dir} && rsync'
        os.system(f'rsync -rv --inplace --progress {self.log_dir} {self.remote_dir}')

    def _add_hparams(self, hparam_dict, metric_dict, hparam_domain_discrete=None, run_name=None):
        """
        Adds hyperparameters and metrics to TensorBoard logs.

        Args:
            hparam_dict (dict): Dictionary of hyperparameters.
            metric_dict (dict): Dictionary of metrics.
            hparam_domain_discrete (dict, optional): Discrete domains for hyperparameters. Defaults to None.
            run_name (str, optional): Name of the run in TensorBoard. Defaults to None.

        Raises:
            TypeError: If `hparam_dict` or `metric_dict` are not dictionaries.
        """
        torch._C._log_api_usage_once("tensorboard.logging.add_hparams")
        if type(hparam_dict) is not dict or type(metric_dict) is not dict:
            raise TypeError('hparam_dict and metric_dict should be dictionary.')
        exp, ssi, sei = hparams(hparam_dict, metric_dict, hparam_domain_discrete)

        self.file_writer.add_summary(exp)
        self.file_writer.add_summary(ssi)
        self.file_writer.add_summary(sei)
        for k, v in metric_dict.items():
            if v is not None:
                self.add_scalar(k, v)

def return_tensorboard_path() -> str:
    """
    Returns the path to the TensorBoard logs directory for the current experiment.

    Returns:
        str: The path to the TensorBoard logs directory.
    """
    default_dir = config.get_env_variable('DEFAULT_DIR')
    dvc_exp_name = config.get_env_variable('DVC_EXP_NAME')
    current_datetime = datetime.datetime.now().strftime('%Y%m%d-%H%M')
    # Set the TUSTU_WRITER_DATE environment variable to the current datetime for the writer to access
    tensorboard_path = Path(f'{default_dir}/logs/tensorboard/{current_datetime}_{dvc_exp_name}')
    tensorboard_path.mkdir(parents=True, exist_ok=True)
    return tensorboard_path

def copy_slurm_logs() -> None:
    """
    Copies the SLURM logs specific to the current experiment from the host directory
    to the temporary experiment directory.

    The SLURM log is identified using the SLURM_JOB_ID environment variable, and the logs are
    copied from the source directory to the destination directory named after the current DVC experiment.

    If the SLURM_JOB_ID is not found, the copying process is skipped.
    """
    default_dir = config.get_env_variable('DEFAULT_DIR')
    current_slurm_job_id = config.get_env_variable('SLURM_JOB_ID')
    dvc_exp_name = config.get_env_variable('DVC_EXP_NAME')
    slurm_logs_source = Path(f'{default_dir}/logs/slurm')
    slurm_logs_destination = Path(f'exp_logs/slurm/_{dvc_exp_name}')
    slurm_logs_destination.mkdir(parents=True, exist_ok=True)
    if current_slurm_job_id is not None:
        for f in slurm_logs_source.iterdir():
            if f.is_file() and f.name.startswith('slurm'):
                slurm_id = f.name.split('-')[1].split('.')[0]
                if slurm_id == current_slurm_job_id:
                    shutil.copy(f, slurm_logs_destination)
                    break
        print(f"Slurm log {current_slurm_job_id} copied to {slurm_logs_destination}")
    else:
        print("No SLURM_JOB_ID found. Skipping copying of SLURM logs.")    
    
def copy_tensorboard_logs() -> None:
    """
    Copies the TensorBoard logs specific to the current experiment from the host directory
    to the temporary experiment directory.

    The logs are copied from the source directory to a destination directory named after the
    current DVC experiment.
    """
    default_dir = config.get_env_variable('DEFAULT_DIR')
    dvc_exp_name = config.get_env_variable('DVC_EXP_NAME')
    tensorboard_logs_source = Path(f'{default_dir}/logs/tensorboard')
    tensorboard_logs_destination = Path(f'exp_logs/tensorboard/{dvc_exp_name}')
    tensorboard_logs_destination.mkdir(parents=True, exist_ok=True)
    for file_path in tensorboard_logs_source.iterdir():
        if file_path.is_file():
            destination_file = tensorboard_logs_destination / file_path.name
            shutil.copy(file_path, destination_file)
    print(f"Tensorboard logs copied to {tensorboard_logs_destination}")


def main():
    copy_slurm_logs()
    copy_tensorboard_logs()


if __name__ == '__main__':
    main()
