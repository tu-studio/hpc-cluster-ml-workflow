#!/bin/bash

#SBATCH -J exp_job
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --ntasks-per-core=1
#SBATCH --cpus-per-task=1
#SBATCH --gres=gpu:tesla:1
#SBATCH --mem=100GB
#SBATCH --time=100:00:00
#SBATCH --partition=gpu
#SBATCH --mail-type=ALL
#SBATCH --mail-user={michael.gh.witte@campus.tu-berlin.de}

ulimit -u 512

## Load necessary modules
module load singularity/4.0.2 
module load nvidia/cuda/12.2 

## Pull the latest container image
singularity pull docker://michaelwitte/ml-pipeline-image:latest 

## Execute inside the singularity container
STORAGE_DEFAULT_DIRECTORY="$PWD" singularity exec --nv --bind $(pwd):/usr/src/app --bind $HOME/.ssh:/root/.ssh ml-pipeline-image_latest.sif sh -c "
  ssh-keyscan github.com >> /root/.ssh/known_hosts &&  # Add GitHub to known hosts to avoid user interaction
  git config --global user.name 'michaelwitte' &&     # Set global Git config for user name
  git config --global user.email 'michael-witte@hotmail.de' &&  # Set global Git config for email
  . /usr/src/cntnrvenv/bin/activate &&                # Activate the environment
  git pull origin main &&
  dvc pull data/raw &&
  dvc exp run &&                                      # Run DVC experiment
  experiment_name=$(tail -f slurm-${SLURM_JOB_ID}.out | grep -oP "Ran experiment\(s\): \K[\w\-]+") &&
  echo "The current experiment is: $experiment_name" &&
  dvc exp branch $experiment_name exp_${experiment_name} &&                    # Create a new branch for the experiment
  git checkout exp_${experiment_name} &&                      # Checkout the new branch
  dvc checkout &&                                    # Checkout the experiment
  git push --set-upstream origin exp_${experiment_name}  &&      # Push the new branch to remote
  dvc push &&
"
