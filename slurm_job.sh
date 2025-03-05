#!/bin/bash

# Copyright 2024 tu-studio
# This file is licensed under the Apache License, Version 2.0.
# See the LICENSE file in the root of this project for details.

# Job name and logs
#SBATCH -J tustu
#SBATCH --output=./logs/slurm/slurm-%j.out

# Resources needed
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --cpus-per-task=16
#SBATCH --gres=gpu:tesla:2
#SBATCH --mem=100GB
#SBATCH --time=10:00:00
#SBATCH --partition=gpu

# Get email notifications for job status
#SBATCH --mail-type=ALL
#SBATCH --mail-user=<your-email-address>

# Default variable values
rebuild_container=false
sif_container=false

# Function to display script usage
usage() {
  echo "Usage: $0 [OPTIONS]"
  echo "Options:"
  echo " -h, --help                Display this help message"
  echo " -b, --rebuild-container   Force the rebuild of the singularity container (default: false)"
  echo " -s, --sif-container       Build the singularity container as SIF (Singularity Image Format) file (default: false)"
}

# Function to handle options and arguments
handle_options() {
  while [ $# -gt 0 ]; do
    case $1 in
      -h | --help)
        usage
        exit 0
        ;;
      -b | --rebuild-container)
        rebuild_container=true
        ;;
      -s | --sif-container)
        sif_container=true
        ;;
      *)
        echo "Invalid option: $1" >&2
        usage
        exit 1
        ;;
    esac
    shift
  done
}

# Main script execution
handle_options "$@"

# Perform the desired actions based on the provided flags and arguments
if [ "$rebuild_container" = true ]; then
  echo "Forcing the rebuild of the singularity container..."
fi

if [ "$sif_container" = true ]; then
  echo "Singularity container format set to SIF (Singularity Image Format) file..."
  echo "When executed, the container will be converted to a temporary sandboxed image. This may take a while..."
fi

# Load necessary modules
module load singularity/4.0.2

# Set environment variables defined in global.env
set -o allexport
source global.env
set +o allexport

# Define DEFAULT_DIR in the host environment
export DEFAULT_DIR="$PWD"

if [ "$sif_container" = true ]; then
  container_extension=".sif"
  container_build_flags=""
else
  container_extension="/"
  container_build_flags="--sandbox"
fi

# Remove existing container if --rebuild-container flag is set
if { [ -d $TUSTU_PROJECT_NAME-image_latest$container_extension ] || [ -f $TUSTU_PROJECT_NAME-image_latest$container_extension ]; } && [ "$rebuild_container" = true ]; then
  echo "Removing the existing container as --rebuild-container flag is set..."
  rm -rf $TUSTU_PROJECT_NAME-image_latest$container_extension
fi

# Build the singularity container from the docker image if it does not exist
if ! { [ -d $TUSTU_PROJECT_NAME-image_latest$container_extension ] || [ -f $TUSTU_PROJECT_NAME-image_latest$container_extension ]; } ; then
  echo "Building the singularity container from docker image..."
  # Pull the latest docker image from Docker Hub and convert it to a singularity image. This will automatically take the a cached image if it exists.
  singularity build $container_build_flags $TUSTU_PROJECT_NAME-image_latest$container_extension docker://$TUSTU_DOCKERHUB_USERNAME/$TUSTU_PROJECT_NAME-image:latest
fi

echo "Starting execution from singularity container..."

# Run the singularity container
singularity exec --nv --bind $DEFAULT_DIR $TUSTU_PROJECT_NAME-image_latest$container_extension ./exp_workflow.sh