# Setup Instructions

**Table of Contents:**
- [1 - Initial Setup](#1---initial-setup)
- [2 - Docker Image](#2---docker-image)
- [3 - DVC Experiment Pipeline](#3---dvc-experiment-pipeline)
- [4 - Tensorboard Metrics](#4---tensorboard-metrics)
- [5 - Test and Debug Locally](#5---test-and-debug-locally)
- [6 - Slurm Job Configuration](#6---slurm-job-configuration)
- [7 - HPC Cluster Setup](#7---hpc-cluster-setup)
- [8 - Test and Debug on the HPC Cluster](#8---test-and-debug-on-the-hpc-cluster)

## 1 - Initial Setup

This section guides you through local project setup. Use your local machine for development and debugging, reserving the cluster primarily for training and minor configurations.

### Create your Git Repository from the Template

- Navigate to the template repository on GitHub.
- Click **Use this template** &rarr; **Create a new repository**.
- Configure the repository settings as needed.
- Clone your new repository:
```sh
git clone git@github.com:<github_user>/<repository_name>.git
```

### Change the Project Name

In your Git repository open the file [global.env](./../global.env) and modify the following variable (the others are changed later):

`TUSTU_PROJECT NAME`: Your Project Name

### Set up a Virtual Environment

   ```sh
   cd <repository_name>
   python3 -m venv venv
   source venv/bin/activate
   pip install dvc torch tensorboard 
   ```
   > **Note**: If you choose a different virtual environment name, update it in [.gitignore](./../.gitignore).

Save the python version of your virtual environment to the global environment file [global.env](./../global.env) (This is necessary for the Docker image build later):

`TUSTU_PYTHON_VERSION`: The Python version required for your project (check with `python --version`).

### Configure your DVC Remote

Choose a [supported storage type](https://dvc.org/doc/command-reference/remote/add#supported-storage-types) and install the required DVC plugin (e.g., for WebDAV):
```sh
pip install dvc_webdav
```
**Quick configuration**: Uses existing config file and only overwrites required parts.     
```sh
dvc remote add -d myremote webdavs://example.com/path/to/storage --force
dvc remote modify --local myremote user 'yourusername'
dvc remote modify --local myremote password 'yourpassword'
```
**Full configuration**: Reinitializes DVC repository and adds all configuration from scratch.
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

- **Sign Up for Docker Hub:** If you don't have an account, register at [Docker Hub](https://app.docker.com/signup?).
- **Configure GitHub Secrets:** In your GitHub repository, go to **Settings** → **Security** → **Secrets and variables** → **Actions** → **New repository secret**, and add secrets for:
   - `DOCKER_USERNAME`: Your Docker Hub username
   - `DOCKER_PASSWORD`: Your Docker Hub password
- **Update Global Environment File:** Edit [global.env](./../global.env)  to set:
   - `TUSTU_DOCKERHUB_USERNAME`: Your Docker Hub username

### Connect SSH Host for Tensorboard (Optional) 

Open your SSH configuration (`~/.ssh/config`) and add your SSH host:
```text
Host yourserveralias
   HostName yourserver.domain.com
   User yourusername
   IdentityFile ~/.ssh/your_identity_file
```  

You can try to log into your server. Enter your password and confirm with 'yes'. Once you logged in succesfully, log out again.
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

In your Git repository open the file [global.env](./../global.env) and modify the following variable:

`TUSTU_TENSORBOARD_HOST`: Your SSH Server Alias
  
## 2 - Create a Docker Image

### Install and freeze dependencies

Install all dependencies needed for your project in your local virtual environment:

```sh
source venv/bin/activate
pip install dependency1 dependency2 ... 
```

Ensure that all dependencies are frozen by updating the requirements.txt file with fixed versions from your virtual environment:

```sh
pip freeze > requirements.txt
```

### Build the Docker Image

For debugging your Docker image locally, install Docker for your operating system / distro. For Windows and macOS, you can install [Docker Desktop](https://www.docker.com/products/docker-desktop/).

To build your Docker image, use the following command in your project directory. The [Dockerfile](../Dockerfile) provided in the template will install the set Python version (cf. [Section 1](#set-up-a-virtual-environment)) and all dependencies from the requirements.txt file on a minimal debian image.

```sh
docker build -t <your_image_name> .
```

### Test the Docker Image

Run the Docker image locally in an interactive shell to test if everything is working as expected:

```sh
docker run -it -rm <your_image_name> /bin/bash
```

### Automated Image Builds with GitHub Actions

Once you have successfully tested your initial Docker image locally, you can use the build and push workflow with GitHub Actions. Remember to always fix the requirements versions you are using before pushing in case some requirements have changed. Also, when using the free docker/build-push action, there is a 14GB storage limit for free public repos for the runner ([About GitHub runners](https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners/about-github-hosted-runners)). The docker image must therefore not exceed a given size. The provided github workflow [docker_image.yml](../.github/workflows/docker_image.yml) will be triggered whenever the [Dockerfile](../Dockerfile), the requirements.txt or the workflow itself have changed and build and push the Docker image to your configured Docker registry.

> **Info:** At the moment the images are only built on ubuntu-latest runners for the x86_64 architecture. If you need to build images for other architectures, change the workflow file accordingly.

## 3 - DVC Experiment Pipeline

This section guides you through setting up the DVC experiment pipeline. The DVC experiment pipeline allows you to manage and version your machine learning workflows, making it easier to track, reproduce, and share your experiments. It also optimizes computational and storage costs by using an internal cache storage to avoid redundant computation of pipeline stages.

> **Info:** For a deeper understanding of DVC, refer to the [DVC Documentation](https://dvc.org/doc).

### Add dataset to the DVC repository / remote

Add data to your experiment pipeline (e.g., raw data) and push it to your DVC remote:

```sh
dvc add data/raw
dvc push
```

> **Info**: The files added with DVC should be Git-ignored, but adding with dvc will create .gitignore files automatically. What git tracks are references with a .dvc suffix (data/raw.dvc). Make sure you add and push the .dvc files to the Git remote at the end of this section.

### Modularize your Codebase

If you started with a Jupyter Notebook or a single python script, split it into separate Python scripts representing different stages (e.g.: preprocess.py, train.py, export.py, ...) and dependencies (e.g.: model.py, ...). This modular approach will enable DVC pipeline integration. Have a look at the example implementation in the [source](../source) directory.

### Integrate Hyperparameter Configuration

- Identify the hyperparameters in your scripts that should be configurable.
- Add the hyperparameters to the [params.yaml](../params.yaml) file, organized by stage or module. Use a `general:` section for shared hyperparameters.
- Instantiate a `Params` object in each time you need to access the required parameters.

```python
# train.py
from utils import config

def main():
   params = config.Params()
   random_seed = params['general']['random_seed']
   batch_size = params['train']['batch_size']
```

### Create DVC experiment pipeline

Manually add your stages to the [dvc.yaml](../dvc.yaml) file:
- `cmd:` Specify the command to run the stage.
- `deps:` Decide which dependencies should launch the stage execution on a change.
- `params:` Include the hyperparameters from [params.yaml](../params.yaml) that should launch the stage execution on a change.
- `out:` Add output directories.
- The last stage should be left as `save_logs`, which will copy the logs to the DVC experiment branch before the experiment ends and push to the remote.
> **Note**: The stage scripts should be able to recreate the output directories, because DVC will delete them at the beginning of each stage.

## 4 - Tensorboard Metrics

To log your machine learning metrics using TensorBoard and enable comparison of DVC experiments, follow the steps below:

### Initialize TensorBoard Logging

- In your training script, import the `logs` module from the `utils` package and create a log directory for the writer using `logs.return_tensorboard_path()`. This function generates a path in the main repository directory under `logs/tensorboard/<dvc_exp_name>` and returns the absolute path needed to instantiate the `CustomSummaryWriter`.
- If you wish to display metrics in TensorBoard’s HParams plugin (which is useful for hyperparameter tuning), initialize a dictionary with the metric names you plan to log.
- Next, create an object from the `logs.CustomSummaryWriter`, which extends the functionality of the standard TensorBoard `SummaryWriter` class for the easier usage of the workflow system of the template. Pass the `params` object (as defined in your training script see  [Integrate Hyperparameter Configuration](#integrate-hyperparameter-configuration)) to the `params` argument. This will automatically log the hyperparameters to the same TensorBoard log file, making them visible in TensorBoard.

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

For detailed information on how to write different types of log data, refer to the official [TensorBoard SummaryWriter Class Documentation](https://pytorch.org/docs/stable/tensorboard.html#torch.utils.tensorboard.writer.SummaryWriter).

Below is an example on how to log scalar metrics and audio examples in the training loop. Ensure that the metric names used with `add_scalar` match those in the metrics dictionary initialized earlier, especially if you want them to appear in the HParams section of TensorBoard. If you want to log data inside of a function, pass the writer as an argument.

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

> **Note:** The `writer.add_hparams` function has been overwritten to not write the hparams in a seperate logfile. It is called by the constructor if the params are set.

### Enable Remote Syncing (Optional)

If you want to utilize the `CustomSummaryWriter`'s ability to transfer data to a remote TensorBoard host via SSH at regular intervals, follow these steps:

- **Configure SSH and Hostname:**
   Ensure your SSH host is configured as described in [Connect SSH Host for Tensorboar (Optional)](#connect-ssh-host-for-tensorboard-optional).
- **Set Sync Intervals:**
   In your [global.env](./../global.env), set the `TUSTU_SYNC_INTERVAL` to a value greater than 0. This enables data transfer via `rsync` to your remote SSH TensorBoard host.
- **Increment Steps:**
   Add `writer.step()` in your epoch train loop to count epochs and trigger syncing at defined intervals.

This process will create a directory (including parent directories) under `$TUSTU_TENSORBOARD_LOGS_DIR/<tustu_project_name>/logs/tensorboard/<dvc_exp_name>` on your SSH server, syncing the log file and updates to this directory. You can change the path in the [global.env](./../global.env) file by setting `TUSTU_TENSORBOARD_LOGS_DIR` to a different location.

## 5 - Test and Debug Locally

We recommend testing and debugging your DVC experiment pipeline locally before running it on the HPC Cluster. This process will help you identify and resolve any issues that may arise during the execution of the pipeline.

### Run the DVC Experiment Pipeline natively

Execute the following command:

```sh
./exp_workflow.sh
```

This script will run the experiment pipeline `dvc exp run` and execute some extra steps like importing the global environment variables and duplicating the repository in a temporary directory to avoid conflicts with the DVC cache when running multiple experiments simultaneously.

### Run the DVC Experiment Pipeline in a Docker Container

To run the Docker container with repository, SSH and Git-gonfig bindings use the following command:

```sh
docker run --rm \
  --mount type=bind,source="$(pwd)",target=/home/app \
  --mount type=bind,source="$HOME/.ssh",target=/root/.ssh \
  --mount type=bind,source="$HOME/.gitconfig",target=/root/.gitconfig \
  <your_image_name> \
  /home/app/exp_workflow.sh
```

## 6 - Slurm Job Configuration

This section covers SLURM Job setup for the HPC-Cluster. SLURM manages resource allocation, which we specify in a batch job script. Our goal is to run the DVC experiment pipeline within a Singularity Container on the nodes, pulled and converted from your DockerHub image. The [slurm_job.sh](../slurm_job.sh) template handles these processes, requiring minimal configuration.

For single GPU nodes, modify these SBATCH directives in [slurm_job.sh](../slurm_job.sh):

In example replace the project name, select memory usage, and set a time limit:

```bash
#SBATCH -J your_project_name
#SBATCH --mem=100GB
#SBATCH --time=10:00:00
```

> **Tip**: Lower time and memory settings are recommended for initial testing, as they affect job prioritization.

> **Note**: SBATCH directives are executed first and can't be easily configured with environment variables.

> **Info**: For detailed information, consult the official [SLURM Documentation](https://slurm.schedmd.com/documentation.html). See [HPC Documentation](https://hpc.tu-berlin.de/doku.php?id=hpc:scheduling:access) for information regarding the [HPC Cluster - ZECM, TU Berlin](https://www.tu.berlin/campusmanagement/angebot/high-performance-computing-hpc).

## 7 - HPC Cluster Setup

This section shows you how to set up your project on the HPC Cluster. It assumes prior configurations are already pushed to the Git remote, thus it focuses on reconfiguring git-ignored items and SSH keys. Additionally, it includes general filesystem and storage configurations that are not project-specific.

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

> **Info:** See [HPC Documentation](https://hpc.tu-berlin.de/doku.php?id=hpc:hardware:beegfs) for information about the filesystem.

Set up a temporary directory on `/scratch` for having more space for temporary files. Then add the `TMPDIR` environment variable to your `.bashrc` so that singularity uses this directory for temporary files. These can get quite large, because singularity uses it for extracting the image and running the container.

```sh
mkdir <username>/tmp
echo 'export TMPDIR=/scratch/<username>/tmp' >> ~/.bashrc
source ~/.bashrc
```

Restrict permissions on your subdirectory (Optional):

```sh
chmod 700 <username>/
```

Assuming you configured Git already on the HPC-Cluster, clone your Git repository to `/scratch/<username>`:

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

> **Warning:** If you don't unload the Python Environment Module, the libraries won't be pip-installed in your virtual environment but in your user site directory!

Configure DVC remote if local configuration is needed for your remote:

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

The logs will be saved in the `logs` directory of your repository. You can monitor the job status with `squeue -u <username>` and check the logs with `cat logs/slurm-<job_id>.out`.

You can also run multiple trainings with parameter grids or predefined sets, modify `multi_submission.py` and execute it:

```sh
python multi_submission.py
```

For more information on running and monitoring jobs, refer to the [User Guide](./USAGE.md).
