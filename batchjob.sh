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

echo "Starting singularity execution..."

# Run the singularity container, bind the current directory to the container's working directory, bind ssh key for git
DEFAULT_DIR="$PWD" singularity exec --nv ml-pipeline-image_latest.sif bash -c '  
  if [ ! -d "$TUSTU_TEMP_PATH" ]; then
    mkdir -p "$TUSTU_TEMP_PATH"
    echo "The directory $TUSTU_TEMP_PATH has been created."
  else
    echo "The directory $TUSTU_TEMP_PATH already exists."
  fi
  mkdir "$TUSTU_TEMP_PATH/$INDEX"

  # Copy all non-gitignored files and config.local to the temporary directory
  {
    git ls-files;
    echo ".dvc/config.local";
  } | rsync -av --files-from=- ./ "$TUSTU_TEMP_PATH/$INDEX"
  echo "All non-gitignored files have been copied to $TUSTU_TEMP_PATH/$INDEX"
  cd $TUSTU_TEMP_PATH/$INDEX

  # Set shared cache directory
  dvc cache dir $PWD/.dvc/cache

  dvc pull 
	  
  # Run the experiment with the specified parameters set by exec_experiment.py as an environment variable
  # If no EXP_PARAMS is empty the default params are chosen
  dvc exp run $EXP_PARAMS &&

  dvc exp push origin &&

  cd .. &&
  rm -rf $INDEX    
  '
