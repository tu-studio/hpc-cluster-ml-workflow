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
Pull the latest docker image from Docker Hub and convert it to a singularity image. Using cached singularity image if nothing changed
singularity pull docker://$TUSTU_DOCKERHUB_USERNAME/$TUSTU_PROJECT_NAME-image:latest 

echo "Starting singularity execution..."

# Run the singularity container, bind the current directory to the container's working directory, bind ssh key for git
DEFAULT_DIR="$PWD" singularity exec --nv ml-pipeline-image_latest.sif bash -c '    
  echo "Checking directory existence..."
  if [ ! -d "../$TUSTU_TEMP_PATH" ]; then
    mkdir -p "../$TUSTU_TEMP_PATH"
    echo "The directory ../$TUSTU_TEMP_PATH has been created."
  else
    echo "The directory ../$TUSTU_TEMP_PATH already exists."
  fi

  mkdir "../$TUSTU_TEMP_PATH/$INDEX"
  echo "Copying files..."
  {
    git ls-files;
    echo ".dvc/config.local";
  } | rsync -av --files-from=- ./ "../$TUSTU_TEMP_PATH/$INDEX"

  cd ../$TUSTU_TEMP_PATH/$INDEX

  echo "Setting DVC cache directory..."
  dvc cache dir $DEFAULT_DIR/.dvc/cache

  echo "Pulling data with DVC..."
  dvc pull
  
  echo "Running experiment..."
  dvc exp run $EXP_PARAMS &&

  echo "Pushing experiment..."
  dvc exp push origin &&

  echo "Cleaning up..."
  cd .. &&
  rm -rf $INDEX		
  '
