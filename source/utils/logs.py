import os
import shutil
import pathlib as Path
import torch
from torch.utils.tensorboard import SummaryWriter
from torch.utils.tensorboard.summary import hparams

# Override the SummaryWriter class to add hyperparameters to the same tensorboard logs and enable metrics as scalar sequences
class CustomSummaryWriter(SummaryWriter):
    def add_hparams(self, hparam_dict, metric_dict, hparam_domain_discrete=None, run_name=None):
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

def create_tensorboard_path(tustu_logs_dir, default_dir, dvc_exp_name) -> str:
    tensorboard_path = os.path.join(default_dir, tustu_logs_dir, 'tensorboard', dvc_exp_name)
    return tensorboard_path 
    
# Copy the experiment specific tensorboard logs from the host directory to the temporary experiment directory
def copy_tensorboard_logs(tensorboard_path, experiment_name) -> None:
    destination_path = os.path.join('exp-logs/tensorboard', experiment_name)
    if not os.path.exists(destination_path):
        os.makedirs(destination_path)
    for file_name in os.listdir(tensorboard_path):
        source_file = os.path.join(tensorboard_path, file_name)
        destination_file = os.path.join(destination_path, file_name)
        shutil.copy(source_file, destination_file)

def copy_slurm_logs(experiment_name, tustu_logs_path) -> None:
    experiment_name = os.environ.get('DVC_EXP_NAME')
    if experiment_name is None:
        raise EnvironmentError("The environment variable 'DVC_EXP_NAME' is not set.")

    destination_path = os.path.join('exp-logs/slurm', experiment_name)

    if not os.path.exists(destination_path):
        os.makedirs(destination_path)

    tustu_logs_path = os.environ.get('TUSTU_LOGS_PATH')
    if tustu_logs_path is None: 
        raise EnvironmentError("The environment variable 'TUSTU_LOGS_PATH' is not set.")
    default_dir = os.environ.get('DEFAULT_DIR')
    if default_dir is None:
        raise EnvironmentError("The environment variable 'DEFAULT_DIR' is not set.")

    slurm_path = os.path.join(default_dir, os.path.join(tustu_logs_path, 'slurm'))

    current_slurm_job_id = os.environ.get('SLURM_JOB_ID')
    if current_slurm_job_id is None:
        raise EnvironmentError("The environment variable 'SLURM_JOB_ID' is not set.")
        
    for f in os.listdir(slurm_path):
        if f.startswith('slurm'):
            slurm_id = f.split('-')[1].split('.')[0]
            if slurm_id == current_slurm_job_id:
                shutil.copy(os.path.join(slurm_path, f), destination_path)
                break

    print(f"Slurm log {current_slurm_job_id} copied to {destination_path}")


if __name__ == '__main__':
    copy_slurm_logs()
