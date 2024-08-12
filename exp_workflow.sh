#!/bin/bash

# Description: This script runs an experiment with DVC within a temporary directory copy and pushes the results to the dvc remote.

# Set environment variables defined in global.env
export $(grep -v '^#' global.env | xargs)

# Define DEFAULT_DIR in the host environment
export DEFAULT_DIR="$PWD"

TUSTU_TMP_DIR=tmp

# Create a temporary directory for the experiment
echo "Checking directory existence..."
if [ ! -d "$TUSTU_TMP_DIR" ]; then
    mkdir -p "$TUSTU_TMP_DIR"
    echo "The directory $TUSTU_TMP_DIR has been created."
else
    echo "The directory $TUSTU_TMP_DIR exists. Using existing directory."
fi &&

# Create a new sub-directory in the temporary directory for the experiment
echo "Creating temporary sub-directory..." &&
# Generate a unique ID with the current timestamp, process ID, and hostname for the sub-directory
UNIQUE_ID=$(date +%s)-$$-$HOSTNAME &&
TUSTU_EXP_TMP_DIR="$TUSTU_TMP_DIR/$UNIQUE_ID" &&
mkdir -p $TUSTU_EXP_TMP_DIR &&

# Copy the necessary files to the temporary directory
echo "Copying files..." &&
{
# Add all git-tracked files
git ls-files;
if [ -f ".dvc/config.local" ]; then
    echo ".dvc/config.local";
fi;
echo ".git";
} | while read file; do
    rsync -aR "$file" $TUSTU_EXP_TMP_DIR;
done &&

# Change the working directory to the temporary sub-directory
cd $TUSTU_EXP_TMP_DIR &&

# Set the DVC cache directory to the shared cache located in the host directory
echo "Setting DVC cache directory..." &&
dvc cache dir $DEFAULT_DIR/.dvc/cache &&

# Pull the data from the DVC remote repository
if [ -f "data/raw.dvc" ]; then
    echo "Pulling data with DVC..." 
    dvc pull data/raw;
fi &&

# Run the experiment with passed parameters. Runs with the default parameters if none are passed.
echo "Running experiment..." &&
dvc exp run $EXP_PARAMS &&

# Push the results to the DVC remote repository
echo "Pushing experiment..." &&
dvc exp push origin &&

# Clean up the temporary sub-directory
echo "Cleaning up..." &&
cd .. &&
rm -rf $UNIQUE_ID