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
#SBATCH --output=./logs/slurm/slurm-%j.out

# Load necessary modules
module load singularity/4.0.2 

# Set environment variables defined in global.env
export $(grep -v '^#' global.env | xargs)

# Remove the previous singularity image if it exists
if [ -f $TUSTU_PROJECT_NAME-image_latest.sif ]; then
    rm $TUSTU_PROJECT_NAME-image_latest.sif
fi
# Pull the latest docker image from Docker Hub and convert it to a singularity image. Using cached singularity image if nothing changed
singularity pull docker://$TUSTU_DOCKERHUB_USERNAME/$TUSTU_PROJECT_NAME-image:latest 

# echo "Cleaning up the logs directory..."
# find ./logs -type f ! -name "slurm-$SLURM_JOB_ID.out" -delete

echo "Starting singularity execution..."

# Run the singularity container, bind the current directory to the container's working directory, bind ssh key for git
STORAGE_DEFAULT_DIRECTORY="$PWD" singularity exec --nv ml-pipeline-image_latest.sif bash -c '
  # Run the experiment with the specified parameters set by exec_experiment.py as an environment variable
  # If $EXP_PARAMS is not set the default value will be used
  dvc exp run --temp $EXP_PARAMS 				
  '
