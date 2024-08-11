import shutil
from pathlib import Path
import torch
from torch.utils.tensorboard import SummaryWriter
from torch.utils.tensorboard.summary import hparams
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))
from utils import config
import os

# Overrides the Tensorboard SummaryWriter class to add hyperparameters to the same tensorboard logs and enable metrics as scalar sequences
class CustomSummaryWriter(SummaryWriter):
    def __init__(self, log_dir, params=None, metrics={}, sync_interval=None, remote_dir=None): 
        super().__init__(log_dir=log_dir)
        if sync_interval is None:
            sync_interval = int(config.get_env_variable('TUSTU_SYNC_INTERVAL'))
        if remote_dir is None:
            remote_dir = f'{config.get_env_variable("TUSTU_TENSORBOARD_HOST")}:Data/{config.get_env_variable("TUSTU_PROJECT_NAME")}/logs/tensorboard'
        
        if params is not None:
            self._add_hparams(hparam_dict=params.flattened_copy(), metric_dict=metrics, run_name=log_dir)
        self.sync_interval = sync_interval
        self.remote_dir = remote_dir   
        self.current_step = 0

    def step(self) -> None:
        self.current_step += 1
        if self.sync_interval != 0:
            if self.current_step % self.sync_interval == 0:
                self.flush()
                os.system(f"rsync -rv --inplace --progress {self.log_dir} {self.remote_dir} --rsync-path='mkdir -p Data/{config.get_env_variable('TUSTU_PROJECT_NAME')}/logs/tensorboard && rsync'")

    def _add_hparams(self, hparam_dict, metric_dict, hparam_domain_discrete=None, run_name=None):
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
    default_dir = config.get_env_variable('DEFAULT_DIR')
    dvc_exp_name = config.get_env_variable('DVC_EXP_NAME')
    return Path(f'{default_dir}/logs/tensorboard/{dvc_exp_name}')

# Copy the experiment specific slurm logs from the host directory to the temporary experiment directory
def copy_slurm_logs() -> None:
    default_dir = config.get_env_variable('DEFAULT_DIR')
    current_slurm_job_id = config.get_env_variable('SLURM_JOB_ID')
    dvc_exp_name = config.get_env_variable('DVC_EXP_NAME')
    slurm_logs_source = Path(f'{default_dir}/logs/slurm')
    slurm_logs_destination = Path(f'exp_logs/slurm/{dvc_exp_name}')
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
    
# Copy the experiment specific tensorboard logs from the host directory to the temporary experiment directory
def copy_tensorboard_logs() -> None:
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
