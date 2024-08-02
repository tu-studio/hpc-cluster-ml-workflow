#!/bin/bash

#SBATCH -J tustu
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --ntasks-per-core=1
#SBATCH --cpus-per-task=1
#SBATCH --gres=gpu:tesla:1
#SBATCH --mem=100GB
#SBATCH --time=10:00:00 
#SBATCH --partition=gpu
#SBATCH --output=./logs/slurm/slurm-%j.out

# Load necessary modules
module load singularity/4.0.2 

# Set environment variables defined in global.env and local.env
export $(grep -v '^#' global.env | xargs)
export $(grep -v '^#' local.env | xargs)

# Define DEFAULT_DIR in the host environment
export DEFAULT_DIR="$PWD"

# Remove the previous singularity image if it exists
if [ -f $TUSTU_PROJECT_NAME-image_latest.sif ]; then
  rm $TUSTU_PROJECT_NAME-image_latest.sif
fi
# Pull the latest docker image from Docker Hub and convert it to a singularity image. Using cached singularity image if nothing changed
singularity pull docker://$TUSTU_DOCKERHUB_USERNAME/$TUSTU_PROJECT_NAME-image:latest 

echo "Starting singularity execution..."

# Run the singularity container
singularity exec --nv --bind $DEFAULT_DIR  $TUSTU_PROJECT_NAME-image_latest.sif bash exp_workflow.sh
