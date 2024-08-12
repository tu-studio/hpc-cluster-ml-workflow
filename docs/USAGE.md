# User Guide

## Local Development

### Data Management with DVC
To track and add new data inputs (e.g. data/raw):
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

As your requirements change, always update
requirements.txt with your fixed versions:

```sh
pip freeze > requirements.txt
````

Docker images are rebuilt and pushed to Docker Hub when `requirements.txt`, `Dockerfile`, or `docker_image.yaml` change. If you are triggering an image build, wait until it is built and pushed before you proceed.

## Launch ML Pipeline

### Accessing the Cluster
Log into the High-Performance Computing (HPC) cluster with your SSH key and go to your repository
```bash
ssh hpc
```
### Sync with your latest changes
```sh
cd /scratch/<username>/<repository>
git pull
```
### Execute Pipeline Jobs
For submitting a single Slurm job:
```bash
sbatch slurm_job.sh
```
To launch multiple trainings with parameter grids or predefined sets, modify `multi_submission.py` and run it:
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
Kill a single job with the slurm job id:
```bash
scancel <slurm_job_id>
```
Kill all jobs from your user:
```bash
scancel -u <user_name>
```

### Remote Monitoring with TensorBoard
To start TensorBoard remotely on the SSH Host to access it in the browser:
```bash
tensorboard --logdir=Data/<tustu_project_name>/logs/tensorboard --path_prefix=/tb1
```
Access TensorBoard via your browser at:
```text
<your_domain>/tb1
```

### Local Monitoring with TensorBoard
Set up a cron job to rsync logs to your repository and start TensorBoard to monitor experiments.
```bash
tensorboard --logdir=logs/tensorboard
```
Access TensorBoard via your browser at:
```text
localhost:6006
```
**Tip**: You can view tensorboard logs in VSCode with an official extension.

## Experiment Retrieval
Get your experiments on your local machine.
```bash
dvc exp pull origin
```
Apply a selected experiment, including all dependencies, to your workspace:
```bash
dvc exp apply <exp_name>
```

