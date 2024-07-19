import os
import shutil

current_slurm_job_id = os.environ.get('SLURM_JOB_ID')
if slurm_job_id is None:
    raise EnvironmentError("The environment variable 'SLURM_JOB_ID' is not set.")
tustu_logs_path = os.environ.get('TUSTU_LOGS_PATH')
if tustu_logs_path is None: 
    raise EnvironmentError("The environment variable 'TUSTU_LOGS_PATH' is not set.")

slurm_path = os.pathjoin(tustu_logs_path, 'slurm')
exp_slurm_path = 'exp-logs/slurm'

if not os.path.exists(exp_slurm_path):
    os.makedirs(exp_slurm_path)

for f in os.listdir(slurm_path):
    slurm_id = f.split('-')[1]
    if slurm_id == current_slurm_job_id:
        shutil.copy(f, exp_slurm_path)


    


