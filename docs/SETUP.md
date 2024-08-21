<!--
Copyright 2024 tu-studio
This file is licensed under the Apache License, Version 2.0.
See the LICENSE file in the root of this project for details.
-->

# Setup Instructions

**Table of Contents:**
- [1 - Initial Setup](#1---initial-setup)
- [2 - Docker Image](#2---docker-image)
- [3 - DVC Experiment Pipeline](#3---dvc-experiment-pipeline)
- [4 - TensorBoard Metrics](#4---tensorboard-metrics)
- [5 - Test and Debug Locally](#5---test-and-debug-locally)
- [6 - Slurm Job Configuration](#6---slurm-job-configuration)
- [7 - HPC Cluster Setup](#7---hpc-cluster-setup)
- [8 - Test and Debug on the HPC Cluster](#8---test-and-debug-on-the-hpc-cluster)

## 1 - Initial Setup

This section will guide you through your initial project setup. Use your local machine for development and debugging, and reserve the cluster primarily for training and minor configurations.

### Create your Git Repository from the Template

- Navigate to the template repository on GitHub.
- Click **Use this template** &rarr; **Create a new repository**.
- Configure the repository settings as needed.
- Clone your new repository:
```sh
git clone git@github.com:<github_user>/<repository_name>.git
```
> **Note**: Replace `<github_user>` and `<repository_name>` with your actual GitHub username and repository name, or copy the URL of your repository from GitHub.
### Change the Project Name

In your Git repository open the file [global.env](./../global.env) and modify the following variable (the others can be changed later):

`TUSTU_PROJECT_NAME`: Your Project Name

### Set up a Virtual Environment

Go to your repository, create a virtual environment and install the required dependencies:

   ```sh
   cd <repository_name>
   python3 -m venv venv
   source venv/bin/activate
   pip install dvc torch tensorboard 
   ```
   > **Note**: If you choose a different virtual environment name, update it in [.gitignore](./../.gitignore).

Save the python version of your virtual environment to the global environment file [global.env](./../global.env) (this is necessary for the Docker image build later):

> **Info**: Check your current version with `python --version`.

`TUSTU_PYTHON_VERSION`: The Python version for your project

### Configure your DVC Remote

Choose a [supported storage type](https://dvc.org/doc/command-reference/remote/add#supported-storage-types) and install the required DVC plugin (e.g., for WebDAV):
```sh
pip install dvc_webdav
```
**Quick configuration**: Uses existing [config](../.dvc/config) file and overwrites only required parts.     
```sh
dvc remote add -d myremote webdavs://example.com/path/to/storage --force
dvc remote modify --local myremote user 'yourusername'
dvc remote modify --local myremote password 'yourpassword'
```
**Full configuration**: Reinitializes DVC repository and adds all configurations from scratch.
```sh
rm -rf .dvc/
dvc init 
dvc remote add -d myremote webdavs://example.com/path/to/storage
dvc remote modify --local myremote user 'yourusername'
dvc remote modify --local myremote password 'yourpassword'
dvc remote modify myremote timeout 600
dvc config cache.shared group
dvc config cache.type symlink
```
> **Info:** For detailed information regarding other storage types, refer to the [DVC documentation](https://dvc.org/doc/command-reference/remote).


### Configure Docker Registry  

- **Sign Up for Docker Hub:** If you do not have an account, register at [Docker Hub](https://app.docker.com/signup?).
- **Configure GitHub Secrets:** In your GitHub repository, go to **Settings** → **Security** → **Secrets and variables** → **Actions** → **New repository secret**, and add secrets for:
   - `DOCKER_USERNAME`: Your Docker Hub username
   - `DOCKER_PASSWORD`: Your Docker Hub password
- **Update Global Environment File:** Edit [global.env](./../global.env)  to set:
   - `TUSTU_DOCKERHUB_USERNAME`: Your Docker Hub username

### Connect SSH Host for TensorBoard (Optional) 

Open your SSH configuration (`~/.ssh/config`) and add your SSH host:
```text
Host yourserveralias
   HostName yourserver.domain.com
   User yourusername
   IdentityFile ~/.ssh/your_identity_file
```  

Log in to your server. Enter your password and confirm. Once you logged in succesfully, log out again:
```sh
ssh yourserveralias
exit
```

Copy your public SSH key to the remote server:
```sh
ssh-copy-id -i ~/.ssh/your_identity_file yourserveralias
``` 

You should now be able to log in without password authentication:
```sh
ssh yourserveralias
```
Modify the following variable in your [global.env](./../global.env):

`TUSTU_TENSORBOARD_HOST`: yourserveralias

  
## 2 - Create a Docker Image

### Install and Freeze Dependencies

Install all the necessary dependencies in your local virtual environment:

```sh
source venv/bin/activate
pip install dependency1 dependency2 ... 
```

Update the requirements.txt file with fixed versions from your virtual environment:

```sh
pip freeze > requirements.txt
```

### Build the Docker Image

To debug your Docker image locally, install Docker for your operating system / distro. For Windows and macOS, you can install [Docker Desktop](https://www.docker.com/products/docker-desktop/).

To build your Docker image, use the following command in your project directory. Substitute the placeholder `<your_image_name>` with a name for your image: 

```sh
docker build -t <your_image_name> .
```

> **Info**: The [Dockerfile](../Dockerfile) provided in the template will install the specified Python version (see [Set Up a Virtual Environment](#set-up-a-virtual-environment)) and all dependencies from the requirements.txt file on a minimal Debian image.


### Test the Docker Image

Run the Docker image locally in an interactive shell to test that everything works as expected:

```sh
docker run -it -rm <your_image_name> /bin/bash
```

### Automated Image Builds with GitHub Actions

After testing your initial Docker image locally, use the GitHub Actions workflow for automatic builds: 
- Make sure your dependency versions are fixed in requirements.txt.
- Push your changes to GitHub and the provided workflow [docker_image.yml](../.github/workflows/docker_image.yml) builds the Docker image and pushes it to your configured Docker registry.
- It is triggered whenever the [Dockerfile](../Dockerfile), the [requirements.txt](../requirements.txt) or the workflow itself is modified.
> **Note**: For the free `docker/build-push-action`, there is a 14GB storage limit for free public repositories on GitHub runners ([About GitHub runners](https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners/about-github-hosted-runners)). Therefore, the Docker image must not exceed this size.

> **Info:** At the moment the images are only built on ubuntu-latest runners for the x86_64 architecture. Modify [docker_image.yml](../.github/workflows/docker_image.yml) if other architectures are required.

## 3 - DVC Experiment Pipeline

This section guides you through setting up the DVC experiment pipeline. The DVC experiment pipeline allows you to manage and version your machine learning workflows, making it easier to track, reproduce, and share your experiments. It also optimizes computational and storage costs by using an internal cache storage to avoid redundant computation of pipeline stages.

> **Info:** For a deeper understanding of DVC, refer to the [DVC Documentation](https://dvc.org/doc).

### Add Dataset to the DVC Repository / Remote

Add data to your experiment pipeline (e.g., raw data) and push it to your DVC remote:

```sh
dvc add data/raw
dvc push
```

> **Info**: The files added with DVC should be Git-ignored, but adding with DVC will automatically create .gitignore files. What Git tracks are references with a .dvc suffix (e.g. data/raw.dvc). Make sure you add and push the .dvc files to the Git remote at the end of this section.

### Modularize your Codebase

If your project started with a Jupyter Notebook or a single python script, split it into separate Python scripts that represent different stages of your pipeline (e.g.: preprocess.py, train.py, export.py, ...) and dependencies (e.g.: model.py, ...). This modular structure is necessary for integrating a DVC pipeline. You can find an example implementation in the [source](../source) directory. 

### Integrate Hyperparameter Configuration

- Identify the hyperparameters in your scripts that should be configurable.
- Add the hyperparameters to the [params.yaml](../params.yaml) file, organized by stage or module. Use a `general:` section for shared hyperparameters.
- Access the required parameters in dict notation after instantiating a `Params` object 

```python
# train.py
from utils import config

def main():
   params = config.Params()
   random_seed = params['general']['random_seed']
   batch_size = params['train']['batch_size']
```

### Create a DVC Experiment Pipeline

Manually add your stages to the [dvc.yaml](../dvc.yaml) file:
- `cmd:` Specify the command to run the stage.
- `deps:` Decide which dependencies should launch the stage execution on a change.
- `params:` Include the hyperparameters from [params.yaml](../params.yaml) that should launch the stage execution on a change.
- `out:` Add output directories.
- The last stage should be left as `save_logs`, which will copy the logs to the DVC experiment branch before the experiment ends and is pushed to the remote.
> **Note**: The stage scripts should be able to recreate the output directories, as DVC deletes them at the beginning of each stage.

For reproducibility, it's essential that the script outputs remain deterministic. To achieve this, ensure that all random number generators in your imported libraries use fixed random seeds. You can do this by using our utility function as follows:

```python
from utils import config
config.set_random_seeds(random_seed)
```
> **Note**: This function only sets seeds for the `random`, `numpy`, `torch` and `scipy` libraries. You can modify this function to include seed setting for any additional libraries or devices that your script relies on.

## 4 - TensorBoard Metrics

To log your machine learning metrics using TensorBoard, and to enable overview and comparison of DVC experiments, follow the steps below:

### Initialize TensorBoard Logging
- In your training script, import the `logs` module from the `utils` package.
- Create a logs directory for TensorBoard logs by calling `logs.return_tensorboard_path()`. 
> **Info**: This function generates a path under `logs/tensorboard/<time_stamp>_<dvc_exp_name>` within the main repository directory and returns the absolute path required to instantiate the `logs.CustomSummaryWriter`.
- If you plan to use TensorBoard’s HParams plugin for hyperparameter tuning, initialize a dictionary with the names of the metrics you intend to log. This setup will allow you to easily monitor and compare hyperparameter performance.
- Create an instance of `logs.CustomSummaryWriter`, which extends the standard TensorBoard `SummaryWriter` class to better support the workflow system of the template. When instantiating, pass the `Params` object (as defined in your training script; see [Integrate Hyperparameter Configuration](#integrate-hyperparameter-configuration)) to the `params` argument. This ensures that the hyperparameters are automatically logged along with other metrics in the same TensorBoard log file, making them available for visualization in TensorBoard.

```python
# train.py
from utils import config
from utils import logs

def main():
   params = config.Params()
   # Create a CustomSummaryWriter object to write the TensorBoard logs
   tensorboard_path = logs.return_tensorboard_path()
   metrics = {'Epoch_Loss/train': None, 'Epoch_Loss/test': None, 'Batch_Loss/train': None} # optional
   writer = logs.CustomSummaryWriter(log_dir=tensorboard_path, params=params, metrics=metrics) # metrics optional
```

### Log Metrics 

For detailed information on how to write different types of log data, refer to the official [PyTorch TensorBoard SummaryWriter Class Documentation](https://pytorch.org/docs/stable/tensorboard.html#torch.utils.tensorboard.writer.SummaryWriter).

The following example shows how to log scalar metrics and audio examples in the training loop. Make sure that the metric names used with `add_scalar` match those in the previously initialized metrics dictionary, especially if you want them to appear in the HParams tab of TensorBoard. If you want to log data within a function, pass the writer as an argument.

```python
for t in range(epochs):
    print(f"Epoch {t+1}\n-------------------------------")
    epoch_loss_train = train_epoch(training_dataloader, model, loss_fn, optimizer, device, writer, epoch=t)
    epoch_loss_test = test_epoch(testing_dataloader, model, loss_fn, device, writer)
    epoch_audio_example = generate_audio_example(model, device, testing_dataloader)
    writer.add_scalar("Epoch_Loss/train", epoch_loss_train, t)
    writer.add_scalar("Epoch_Loss/test", epoch_loss_test, t)
    writer.add_audio("Audio_Pred/test", epoch_audio_example, t, sample_rate=44100)
    writer.step() # optional for remote syncing (next section)
```

> **Note:** The `writer.add_hparams` function has been overwritten to avoid writing the hyperparameters to a separate logfile. It is automatically called by the constructor when the params are passed.

### Enable Remote Syncing (Optional)

If you want to use the `CustomSummaryWriter`'s ability to transfer data to a remote TensorBoard host via SSH at regular intervals, follow these steps:

- Ensure your SSH host is configured as described in [Connect SSH Host for Tensorboard (Optional)](#connect-ssh-host-for-tensorboard-optional).
- In your [global.env](./../global.env), set the `TUSTU_SYNC_INTERVAL` to a value greater than 0. This enables data transfer via `rsync` to your remote SSH TensorBoard host.
- Add `writer.step()` in your epoch train loop to count epochs and trigger syncing at defined intervals.

This process creates a directory (including parent directories) under `<tustu_tensorboard_logs_dir>/<tustu_project_name>/logs/tensorboard/` on your SSH server and synchronises the log file and its updates to this directory. You can change the base directory in the [global.env](./../global.env) file by setting `TUSTU_TENSORBOARD_LOGS_DIR` to a different location.

## 5 - Test and Debug Locally

We recommend that you test and debug your DVC experiment pipeline locally before running it on the HPC cluster. This process will help you identify and resolve any problems that may occur during pipeline execution.

### Run the DVC Experiment Pipeline Natively

Execute the following command to run the pipeline:

```sh
./exp_workflow.sh
```

This shell script runs the experiment pipeline (`dvc exp run`) and performs some extra steps such as importing the global environment variables and duplicating the repository into a temporary directory to avoid conflicts with the DVC cache when running multiple experiments simultaneously.

### Run the DVC Experiment Pipeline in a Docker Container

To run the Docker container with repository, SSH and Git-gonfig bindings use the following command with the appropriate image name substituted for the placeholder `<your_image_name>`:

```sh
docker run --rm \
  --mount type=bind,source="$(pwd)",target=/home/app \
  --mount type=bind,source="$HOME/.ssh",target=/root/.ssh \
  --mount type=bind,source="$HOME/.gitconfig",target=/root/.gitconfig \
  <your_image_name> \
  /home/app/exp_workflow.sh
```

## 6 - SLURM Job Configuration

This section covers setting up SLURM jobs for the HPC cluster. SLURM manages resource allocation for your task, which we will specify in a batch job script. Our goal is to run the DVC experiment pipeline inside a Singularity Container on the nodes that have been pulled and converted from your DockerHub image. The batch job script template [slurm_job.sh](../slurm_job.sh) handles these processes and requires minimal configuration.

For single GPU nodes, modify the SBATCH directives for your project name, memory usage and time limit shown in the example below in [slurm_job.sh](../slurm_job.sh):

```bash
#SBATCH -J your_project_name
#SBATCH --mem=100GB
#SBATCH --time=10:00:00
```

> **Tip**: For initial testing, consider using lower time and memory settings to get higher priority in the queue.

> **Note**: SBATCH directives are executed first and can not be easily configured with environment variables.

> **Info**: For detailed information, consult the official [SLURM Documentation](https://slurm.schedmd.com/documentation.html). See [HPC Documentation](https://hpc.tu-berlin.de/doku.php?id=hpc:scheduling:access) for information regarding the [HPC Cluster - ZECM, TU Berlin](https://www.tu.berlin/campusmanagement/angebot/high-performance-computing-hpc).

## 7 - HPC Cluster Setup

This section shows you how to set up your project on the HPC Cluster. It assumes that previous configurations have already been pushed to the Git remote, so it focuses on reconfiguring Git-ignored items and SSH keys. It also covers general filesystem and storage configurations that are not project specific.

### SSH into the HPC Cluster

```sh
ssh hpc
```

> **Tip:** We recommend using an SSH config for faster access. For general info on accessing the [HPC Cluster - ZECM, TU Berlin](https://www.tu.berlin/campusmanagement/angebot/high-performance-computing-hpc) info see [HPC Documentation](https://hpc.tu-berlin.de/doku.php?id=hpc:scheduling:access).

### Initial Setup

Create a personal subdirectory on `/scratch`, since space is limited on the user home directory:

```sh
cd /scratch
mkdir <username>
```

> **Info:** See [HPC Documentation](https://hpc.tu-berlin.de/doku.php?id=hpc:hardware:beegfs) for general information about the filesystem on [HPC Cluster - ZECM, TU Berlin](https://www.tu.berlin/campusmanagement/angebot/high-performance-computing-hpc).

Set up a temporary directory on `/scratch` to get more space for temporary files. Then add the `TMPDIR` environment variable to your `.bashrc` so that singularity uses this directory for temporary files. These can get quite large as singularity uses them to extract the image and run the container.

```sh
mkdir <username>/tmp
echo 'export TMPDIR=/scratch/<username>/tmp' >> ~/.bashrc
source ~/.bashrc
```

Restrict permissions on your subdirectory (Optional):

```sh
chmod 700 <username>/
```

Assuming you have already configured Git on the HPC cluster, clone your Git repository to `/scratch/<username>`:

```sh
cd <username>
git clone git@github.com:<github_user>/<repository_name>.git
```

Set up a virtual environment:

```sh
cd <REPOSITORY_NAME>
module load python
python3 -m venv venv
module unload python
source venv/bin/activate
pip install dvc
```

> **Warning:** If you don't unload the Python environment module, the libraries won't be pip-installed into your virtual environment but into your user site directory!

Configure DVC remote if local configuration is required:

```sh
dvc remote modify --local myremote user 'yourusername'
dvc remote modify --local myremote password 'yourpassword'
```

Connect Tensorboard Host (Optional):
Repeat Steps 1-4 of the Section [Connect SSH Host for Tensorboard (Optional)](#connect-ssh-host-for-tensorboard-optional)

## 8 - Test and Debug on the HPC Cluster

You can run the DVC experiment pipeline on the HPC Cluster by submitting a single SLURM job:

```sh
sbatch slurm_job.sh
```

The logs are stored in the `logs` directory of your repository. You can monitor the job status with `squeue -u <username>` and check the logs with `cat logs/slurm/slurm-<job_id>.out` or the tail with `tail -f logs/slurm/slurm-<job_id>.out`.

To run multiple submissions with a parameter grid or predefined parameter sets, modify [multi_submission.py](../multi_submission.py) and run:

```sh
python multi_submission.py
```

For more information on running and monitoring jobs, refer to the [User Guide](./USAGE.md).
