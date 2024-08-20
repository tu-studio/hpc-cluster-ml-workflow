<!--
Copyright 2024 tu-studio
This file is licensed under the Apache License, Version 2.0.
See the LICENSE file in the root of this project for details.
-->

# User Guide

## Adding data to DVC remote

To track and add new data inputs (e.g., `data/raw`):

```sh
dvc add data/raw
dvc push
```

>**Note**: Only necessary if you want to track new data inputs that are not already declared in the [dvc.yaml](../dvc.yaml) file as outputs of a stage.

## Update Docker Image / Dependencies

As your requirements change, always update `requirements.txt` with your fixed versions:

```sh
pip freeze > requirements.txt
```

Docker images are automatically rebuilt and pushed to Docker Hub when `requirements.txt`, `Dockerfile`, or `docker_image.yml` are updated by the GitHub workflow. If you trigger an image build, ensure it is completed and pushed before proceeding.

**Note**: On the HPC cluster, the Docker image is automatically pulled and converted to a Singularity image with the command `singularity pull docker://<your_image_name>` in the `slurm_job.sh` script.

## Launch ML Pipeline

### Locally natively or with Docker

To run the entire pipeline locally, execute the following command:

```sh
# natively
./exp_workflow.sh
# with Docker
docker run --rm \
  --mount type=bind,source="$(pwd)",target=/home/app \
  --mount type=bind,source="$HOME/.ssh",target=/root/.ssh \
  --mount type=bind,source="$HOME/.gitconfig",target=/root/.gitconfig \
  <your_image_name> \
  /home/app/exp_workflow.sh
```

### On the HPC Cluster

Log into the High-Performance Computing (HPC) cluster using your SSH config and key and navigate to your repository:

```sh
ssh hpc
cd /scratch/<username>/<repository>
git pull # optionally pull the latest changes you have done locally
```

Execute Pipeline Jobs either individually or in parallel. To launch multiple trainings with parameter grids or predefined sets, modify `multi_submission.py`:

```sh
# submit a single Slurm job:
sbatch slurm_job.sh
# submit multiple Slurm jobs:
venv/bin/python multi_submission.py
```

## Monitoring and Logs

### Slurm Job Monitoring

Check the status of all jobs associated with your user account:

```sh
squeue -u <user_name>
```

Monitor Slurm logs in real-time:

```sh
cd logs/slurm
tail -f slurm-<slurm_job_id>.out
```

To kill a single job using the Slurm job ID or user:

```sh
# Per job id
scancel <slurm_job_id>
# Per user
scancel -u <user_name>
```

### Remote Monitoring with TensorBoard

To start TensorBoard remotely on the SSH Host and access it in your browser:

```sh
tensorboard --logdir=Data/<tustu_project_name>/logs/tensorboard --path_prefix=/tb1
```

Access TensorBoard via your browser at:

```text
<your_domain>/tb1
```

### Local Monitoring with TensorBoard

Set up a cron job to rsync logs to your tensorboard logs and start TensorBoard to monitor experiments:

```sh
tensorboard --logdir=logs/tensorboard
```

Access TensorBoard via your browser at:

```text
localhost:6006
```

> **Tip**: You can also view TensorBoard logs in VSCode using the official extension.

## DVC Experiment Retrieval

Each time we run the pipeline, DVC creates a new experiment. These are saved as custom git references that can be retrieved and applied to your workspace. These references do not appear in the git log, but are stored in the `.git/refs/exps` directory and can be pushed to the remote git repository. This is done automatically at the end of the [exp_workflow.sh](../exp_workflow.sh) with `dvc exp push origin`. All outputs and dependencies are stored in the `.dvc/cache` directory and pushed to the remote dvc storage when the experiment is pushed. Since we create a new temporary copy of the repository for each pipeline run (and delete it at the end), the experiments will not automatically appear in the main repository.

To retrieve, view, and apply an experiment, do the following (either locally or on the HPC cluster)

```sh
# Get all experiments from remote
dvc exp pull origin
# List experiments
dvc exp show
# Apply a specific experiment
dvc exp apply <exp_name>.
```

> **Note**: By default, experiments are bound to the git commit when they were run. Therefore the commands `dvc exp pull` and `show` will work on experiments from the same commit as when the experiment was created. To pull, show or apply experiments from a different commit, you can use flags defined in the [DVC documentation](https://dvc.org/doc/command-reference/experiments).

> **Tip**: You can also get the git ref hash of the experiment from `dvc exp show` and do a git diff.
