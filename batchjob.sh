#!/bin/bash

#SBATCH -J exp_job
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --ntasks-per-core=1
#SBATCH --cpus-per-task=1
#SBATCH --gres=gpu:tesla:1
#SBATCH --mem=100GB
#SBATCH --time=1:00:00 
#SBATCH --partition=gpu
#SBATCH --output=./logs/slurm-%j.out

ulimit -u 512

# Load necessary modules
module load singularity/4.0.2 
module load nvidia/cuda/12.2 

# Check and pull the latest container image
if [ -f ml-pipeline-image_latest.sif ]; then
    rm ml-pipeline-image_latest.sif
fi
singularity pull docker://michaelwitte/ml-pipeline-image:latest 

echo "Cleaning up the logs directory..."
find ./logs -type f ! -name "slurm-$SLURM_JOB_ID.out" -delete

echo "Starting singularity execution..."

# Run the singularity container, bind the current directory to the container's working directory, bind ssh key for git
STORAGE_DEFAULT_DIRECTORY="$PWD" singularity exec --nv --bind $(pwd):/usr/src/app --bind $HOME/.ssh:/root/.ssh ml-pipeline-image_latest.sif bash -c '
  # Add the github.com host key to the known hosts file
  ssh-keyscan github.com >> /root/.ssh/known_hosts &&
  # Set the git user name and email
  git config --global user.name "michaelwitte" &&     
  git config --global user.email "michael-witte@hotmail.de" && 
  # Activate the virtual environment, located at a different path than the containers working directory 
  source /usr/src/cntnrvenv/bin/activate &&                
  # Pull the latest raw data for the pipeline and run the experiment
  dvc pull data/raw &&
  dvc exp run &&
  # Wait for the experiment to finish and parse the experiment name
  sleep 5 &&
  experiment_name=$(grep -oP "Ran experiment\(s\): \K[\w\-]+" logs/slurm-$SLURM_JOB_ID.out) &&
  # Promote the current experiment to a new git branch 
  dvc exp branch $experiment_name "exp_$experiment_name" &&
  # Check out the new branch, force the checkout to overwrite the current main branch
  git checkout "exp_$experiment_name" --force &&                
  # Track the log file with DVC
  dvc add logs/slurm-$SLURM_JOB_ID.out &&
  git add logs/slurm-$SLURM_JOB_ID.out.dvc &&
  git commit -m "Add experiment logs for $experiment_name" &&
  # Push the new branch to the remote repository
  git push --set-upstream origin "exp_$experiment_name" &&     
  dvc push &&
  git checkout main 						
  '
