# Setup Instructions

**Table of Contents:**
- [1 - Project Setup](#1---project-setup)
- [2 - DVC Experiment Pipeline](#2---dvc-experiment-pipeline)
- [3 - Tensorboard Metrics](#3---tensorboard-metrics)
- [4 - Docker Image](#4---docker-image)
- [5 - HPC Cluster Setup](#5---project-setup-hpc-cluster)
- [6 - Slurm Job Configuration](#6---slurm-job-configuration)

## 1 - Project Setup

This section guides you through setting up your project locally.

### Create your Git Repository from the Template

- Navigate to the template repository on GitHub.
- Click **Use this template** &rarr; **Create a new repository**.
- Configure repository settings as needed.
    <!-- > **Info**: For detailed information, refer to the [GitHub documentation](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template#creating-a-repository-from-a-template). -->
- Clone your new repository:
```sh
git clone git@github.com:<github_user>/<repository_name>.git
```

### Change Project Name

Modify the environment variable `TUSTU_PROJECT_NAME` in [global.env](./../global.env)

### Set up a Virtual Environment 

   ```sh
   cd <repository_name>
   python3 -m venv venv
   source venv/bin/activate
   pip install dvc torch tensorboard 
   ```
   > **Note**: If you choose a different virtual environment name, update it in [.gitignore](./../.gitignore).

### Configure DVC Remote

If you are part of the Audio Communication Group - TU Berlin, please contact studio@ak.tu-berlin.de for access to our SSH Remote Data Storage.

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
> **Info:** For information regarding other storage types, refer to the [DVC documentation](https://dvc.org/doc/command-reference/remote).


### Configure Docker Registry  

- **Sign Up for Docker Hub:** If you don't have an account, register at [Docker Hub](https://app.docker.com/signup?).
- **Configure GitHub Secrets:** In your GitHub repository, go to **Settings** → **Security** → **Secrets and variables** → **Actions** → **New repository secret**, and add secrets for:
   - `DOCKER_USERNAME`: Your Docker Hub username
   - `DOCKER_PASSWORD`: Your Docker Hub password
- **Update Local Environment File:** Edit [global.env](./../global.env)  to set:
   - `TUSTU_DOCKERHUB_USERNAME`: Your Docker Hub username
   - `TUSTU_PYTHON_VERSION`: The Python version required for your project (check with `python3 --version`).

### Connect SSH Host for Tensorboard (Optional) 

If you are part of the [Audio Communication Group - TU Berlin](https://www.tu.berlin/ak), please contact studio@ak.tu-berlin.de for access to our SSH Host for tensorboard.

Open your SSH configuration (~/.ssh/config) and add your SSH host:
```text
Host yourserveralias
HostName yourserver.domain.com
User yourusername
IdentityFile ~/.ssh/your_identity_file
```  

SSH into your server, enter your password and confirm with 'yes'. Once you logged in succesfully, log out again. 
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
  

### Commit your Changes

```sh
git add .
git commit -m "General project configuration"
```


## 2 - DVC Experiment Pipeline 

This section guides you through setting up the DVC Experiment Pipeline. The DVC experiment pipeline allows you to manage and version your machine learning workflows, making it easier to track, reproduce, and share your experiments. It also optimizes computational and storage costs by using an internal cache system to avoid redundant computation of pipeline stages.

> **Info:** For a deeper understanding of DVC, refer to the [DVC Documentation](https://dvc.org/doc).

### Prepare Your Codebase

- **Moduralize**: If you started with a Jupyter Notebook or a single python script, split it into separate Python scripts representing different stages or dependencies (e.g.: preprocess, augmentation, featurize, train, model, export, evaluate). This modular approach will enable DVC pipeline integration. 
- **Install Dependencies**: Install all the dependencies needed for your project in your local virtual environment.

### Integrate Hyperparameter Configuration

- **Identify Hyperparameters**: Identify the hyperparameters in your scripts that should be configurable.
- **Add to params.yaml**: Add the hyperparameters to the [params.yaml](../params.yaml) file, organized by stage or module. Use a `general:` section for shared hyperparameters.
- **Use the Params Class**: Instantiate a `Params` object in each stage script to access the required parameters:

```python
# train.py
from utils import config

def main():
   params = config.Params()
   random_seed = params['general']['random_seed']
   batch_size = params['train']['batch_size']
```

### Prepare the Pipeline 

**Add Pipeline Input**: Add an input to your experiment pipeline (e.g., raw data) and push it to your DVC remote:

```sh
dvc add data/raw
dvc push
```

**Configure dvc.yaml**: Manually add your stages to the [dvc.yaml](../dvc.yaml) file:
- Specify the command to execute the stage under `cmd:`.
- Decide which dependencies should retrigger the stage on a change and add them to `deps:`.
- Include the hyperparameters from params.yaml that should retrigger the stage on a change under `params:`.
- Add output directories under `out:` 
- The last stage should be left as `save_logs`, which will copy the experiment-specific logs to the DVC experiment branch before termination and push them to the remote.
> **Note**: The stage scripts should be able to recreate the output directories, because DVC will delete them at the beginning of each stage.
**Test and Debug Locally**: If possible, test and debug the DVC pipeline with minimal examples on a local CPU or other available device using the `$ source exp_workflow.sh` command.

### Commit your Changes

```sh
git add .
git commit -m "Initial DVC pipeline configuration"
```   

## 3 - Tensorboard Metrics

To log your machine learning metrics using TensorBoard, and also enable comparison of DVC experiments, follow the steps below:

### Initialize TensorBoard Logging

- In your training script, import the `logs` module from the `utils` package and create a log directory for the writer using `logs.return_tensorboard_path()`. This function generates a path in the main repository directory under `logs/tensorboard/<dvc_exp_name>` and returns the absolute path needed to instantiate the `CustomSummaryWriter`.
- If you wish to display metrics in TensorBoard’s HParams plugin (which is useful for hyperparameter tuning), initialize a dictionary with the metric names you plan to log.
- Next, create an object from the `logs.CustomSummaryWriter`, which extends the functionality of the standard TensorBoard `SummaryWriter` class for the easier usage of the workflow system of the template. Pass the `params` object (as defined in your training script see  [Integrate Hyperparameter Configuration](#integrate-hyperparameter-configuration)) to the `params` argument. This will automatically log the hyperparameters to the same TensorBoard log file, making them visible in TensorBoard.

```python
# train.py
from utils import logs

def main():
   # Create a CustomSummaryWriter object to write the TensorBoard logs
   tensorboard_path = logs.return_tensorboard_path()
   metrics = {'Epoch_Loss/train': None, 'Epoch_Loss/test': None, 'Batch_Loss/train': None}
   writer = logs.CustomSummaryWriter(log_dir=tensorboard_path, params=params, metrics=metrics)
```

### Log Metrics 

For detailed information on how to write different types of log data, refer to the [TensorBoard SummaryWriter Class Documentation](https://pytorch.org/docs/stable/tensorboard.html#torch.utils.tensorboard.writer.SummaryWriter).
> **Note:** `writer.add_hparams` is no longer required, as the child class `CustomSummaryWriter` used for this workflow automatically manages the logging of dvc hyperparameters along with metrics in a way that makes them displayable in the HParams plugin.

Below is an example on how to log scalar metrics and audio examples in the training loop. Ensure that the metric names used with `add_scalar` match those in the metrics dictionary initialized earlier, especially if you want them to appear in the HParams section of TensorBoard.

```python
for t in range(epochs):
    print(f"Epoch {t+1}\n-------------------------------")
    epoch_loss_train = train_epoch(training_dataloader, model, loss_fn, optimizer, device, writer, epoch=t)
    epoch_loss_test = test_epoch(testing_dataloader, model, loss_fn, device, writer)
    epoch_audio_example = generate_audio_example(model, device, testing_dataloader)
    writer.add_scalar("Epoch_Loss/train", epoch_loss_train, t)
    writer.add_scalar("Epoch_Loss/test", epoch_loss_test, t)
    writer.add_audio("Audio_Pred/test", epoch_audio_example, t, sample_rate=44100)
```

### Enable Remote Syncing (Optional)

If you want to utilize the `CustomSummaryWriter`'s ability to transfer data to a remote TensorBoard host via SSH at regular intervals, follow these steps:

- **Configure SSH and Hostname:**
   Ensure your SSH key is configured and the hostname is added to your system. The hostname should also be added to [global.env](./../global.env)  as described in [Connect SSH Host for Tensorboar (Optional)](#connect-ssh-host-for-tensorboard-optional).
- **Set Sync Intervals:**
   In your [global.env](./../global.env), set the `TUSTU_SYNC_INTERVAL` to a value greater than 0. This enables data transfer via `rsync` to your remote SSH TensorBoard host.
- **Increment Steps:**
   Add `writer.step()` in your epoch train loop to count epochs and trigger syncing at defined intervals.

This process will create a directory (including parent directories) under `Data/<tustu_project_name>/logs/tensorboard/<dvc_exp_name>` on your SSH server, syncing the log file and updates to this directory.

### Commit your Changes

Once tested tensorboard logging locally commit your changes. Refer to the User Guide on how to launch tensorboard display.

>**Tip**: If you are using VSCode, we remommend you to install and use the official [TensorBoard VSCode Extension](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.tensorboard).

```sh
git add .
git commit -m "Add TensorBoard logging"
```   

## 4 - Docker Image

### Prepare the Docker Environment

Before building your Docker image, ensure all dependencies are set by updating the requirements.txt file with fixed versions from your virtual environment:

   ```sh
   pip freeze > requirements.txt
   ```

### Build and Debug the Docker Image

For building and debugging your Docker image, we recommended to install [Docker Desktop](https://www.docker.com/products/docker-desktop/). 

To build your Docker image, use the following command in your project directory:

```sh
docker build -t <your_image_name> .
```

### Running the Docker Container

To run the Docker container with repository, SSH and Git-gonfig bindings use the following command:

```sh
docker run --rm \
  --mount type=bind,source="$(pwd)",target=/home/app \
  --mount type=bind,source="$HOME/.ssh",target=/root/.ssh \
  --mount type=bind,source="$HOME/.gitconfig",target=/root/.gitconfig \
  <your_image_name> \
  /home/app/exp_workflow.sh
```

### Automated Image Builds with GitHub Actions

Once you have successfully tested your initial Docker image locally, you can utilize the build and push workflow with GitHub Actions. Remember to always fix the requirement versions you use before pushing, if some requirements changed. Also using the free docker/build-push-action there is a limit of 20 GB for the image:

   ```sh
   pip freeze > requirements.txt
   ```

**Commit and Push Changes:** Push your changes to your GitHub repository. Since the requirements have changed, this will trigger the build action and automatically push the Docker image to your configured Docker registry.

   ```sh
   git add .
   git commit -m "Update environment setup"
   git push origin 
   ```


## 5 - Project Setup: HPC Cluster 

This section guides you through setting up your project on the HPC Cluster, enabling resource usage while synchronizing with local development via Git, DVC, and Docker remotes. It assumes prior configurations are already pushed to the Git remote, thus it focuses on reconfiguring git-ignored items and SSH keys. Additionally, it includes general filesystem and storage configurations that are not project-specific.

Assuming you have access to the HPC Cluster:

### SSH into the HPC Cluster
   ```sh
   ssh hpc
   ````
   > **Tip:** We recommend using an SSH key for faster access. See [HPC Documentation](https://hpc.tu-berlin.de/doku.php?id=hpc:scheduling:access) for general information on accessing the [HPC Cluster - ZECM, TU Berlin](https://www.tu.berlin/campusmanagement/angebot/high-performance-computing-hpc). 

### Initial Setup

Create a personal subdirectory on `/scratch`: 
   ```sh
   cd /scratch
   mkdir <username>
   ```
   > **Info:** See [HPC Documentation](https://hpc.tu-berlin.de/doku.php?id=hpc:hardware:beegfs) for information about the filesystem.

Set up a temporary directory on `/scratch`
   ```sh
   mkdir <username>/tmp
   echo 'export TMPDIR=/scratch/<username>/tmp' >> ~/.bashrc
   source ~/.bashrc
   ```

Restrict permissions on your subdirectory (Optional):
   ```sh
   chmod 700 <username>/
   ```
### Project Setup

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

Configure DVC remote:
   ```sh
      dvc remote modify --local myremote user 'yourusername'
      dvc remote modify --local myremote password 'yourpassword'
   ```
Connect Tensorboard Host 

Repeat Steps 1-4 of the Section [Connect SSH Host for Tensorboard (Optianal)](#connect-ssh-host-for-tensorboard-optional)


## 6 - Slurm Job Configuration

This section covers SLURM Job setup for the HPC-Cluster. SLURM manages resource allocation, which we specify in a batch job script. Our goal is to run the DVC experiment pipeline within a Singularity Container on the nodes, pulled and converted from your DockerHub image. The [slurm_job.sh](../slurm_job.sh) template handles these processes, requiring minimal configuration.

For single GPU nodes, modify these SBATCH directives in [slurm_job.sh](../slurm_job.sh):

Replace project name:
```bash
#SBATCH -J your_project_name
```

Set memory usage:
```bash
#SBATCH --mem=100GB
```

Set time limit:
```bash
#SBATCH --time=10:00:00
```

> **Tip**: Lower time and memory settings are recommended for initial testing, as they affect job prioritization. 

> **Note**: SBATCH directives are executed first and can't be easily configured with environment variables.

> **Info**: For detailed information, consult the official [SLURM Documentation](https://slurm.schedmd.com/documentation.html). See [HPC Documentation](https://hpc.tu-berlin.de/doku.php?id=hpc:scheduling:access) for information regarding the [HPC Cluster - ZECM, TU Berlin](https://www.tu.berlin/campusmanagement/angebot/high-performance-computing-hpc).
