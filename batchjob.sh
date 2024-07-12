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

ulimit -u 512

# Load necessary modules
module load singularity/4.0.2 
module load nvidia/cuda/12.2 

# Check and pull the latest container image
if [ -f ml-pipeline-image_latest.sif ]; then
    rm ml-pipeline-image_latest.sif
fi
singularity pull docker://michaelwitte/ml-pipeline-image:latest 

echo "Starting singularity execution..."

STORAGE_DEFAULT_DIRECTORY="$PWD" singularity exec --nv --bind $(pwd):/usr/src/app --bind $HOME/.ssh:/root/.ssh ml-pipeline-image_latest.sif bash -c '
  ssh-keyscan github.com >> /root/.ssh/known_hosts &&
  git config --global user.name "michaelwitte" &&     
  git config --global user.email "michael-witte@hotmail.de" &&  
  source /usr/src/cntnrvenv/bin/activate &&                
  dvc pull data/raw &&
  dvc exp run &&
  sleep 5 &&
  experiment_name=$(grep -oP "Ran experiment\(s\): \K[\w\-]+" slurm-$SLURM_JOB_ID.out) &&
  dvc exp branch $experiment_name "exp_$experiment_name" &&
  git checkout "exp_$experiment_name" --force &&
  dvc checkout &&
  git push --set-upstream origin "exp_$experiment_name"  &&      # Push the new branch to remote
  dvc push
  '
