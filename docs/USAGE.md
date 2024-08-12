# User Guide

## Local Development

### Data Management with DVC
To track and add new data inputs (e.g., `data/raw`):
```bash
dvc add data/raw
dvc push
```

### Version Control with Git
To track and add code and configuration changes:
```bash
git add .
git commit -m "Update: Increased dataset size"
git push
```

### Docker Image Automation

As your requirements change, always update `requirements.txt` with your fixed versions:
```bash
pip freeze > requirements.txt
```

- Docker images are automatically rebuilt and pushed to Docker Hub when `requirements.txt`, `Dockerfile`, or `docker_image.yaml` are updated.
- If you trigger an image build, ensure it is completed and pushed before proceeding.

## Launch ML Pipeline

### Accessing the Cluster
Log into the High-Performance Computing (HPC) cluster using your SSH key and navigate to your repository:
```bash
ssh hpc
```

### Sync with Your Latest Changes
```bash
cd /scratch/<username>/<repository>
git pull
```

### Execute Pipeline Jobs
To submit a single Slurm job:
```bash
sbatch slurm_job.sh
```
To launch multiple trainings with parameter grids or predefined sets, modify `multi_submission.py` and execute it:
```bash
venv/bin/python multi_submission.py
```

## Monitoring and Logs

### Job Status Monitoring
Check the status of all jobs associated with your user account:
```bash
squeue -u <user_name>
```

### Viewing Slurm Logs
Monitor Slurm logs in real-time:
```bash
cd logs/slurm
tail -f slurm-<slurm_job_id>.out
```

### Killing Jobs
To kill a single job using the Slurm job ID:
```bash
scancel <slurm_job_id>
```
To kill all jobs associated with your user:
```bash
scancel -u <user_name>
```

### Remote Monitoring with TensorBoard
To start TensorBoard remotely on the SSH Host and access it in your browser:
```bash
tensorboard --logdir=Data/<tustu_project_name>/logs/tensorboard --path_prefix=/tb1
```
Access TensorBoard via your browser at:
```text
<your_domain>/tb1
```

### Local Monitoring with TensorBoard
Set up a cron job to rsync logs to your repository and start TensorBoard to monitor experiments:
```bash
tensorboard --logdir=logs/tensorboard
```
Access TensorBoard via your browser at:
```text
localhost:6006
```
> **Tip**: You can also view TensorBoard logs in VSCode using the official extension.

## Experiment Retrieval
To retrieve your experiments on your local machine:
```bash
dvc exp pull origin
```
To apply a selected experiment, including all dependencies, to your workspace:
```bash
dvc exp apply <exp_name>
```

