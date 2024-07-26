# Description: This script runs an experiment with DVC within a temporary directory copy and pushes the results to the dvc remote repository.

# Create a temporary directory for the experiment
echo "Checking directory existence..."
if [ ! -d "$TUSTU_TEMP_DIR" ]; then
    mkdir -p "$TUSTU_TEMP_DIR"
    echo "The directory $TUSTU_TEMP_DIR has been created."
else
    echo "The directory $TUSTU_TEMP_DIR exists. Using existing directory."
fi &&

# Create a new sub-directory in the temporary directory for the experiment
if [ -z "$INDEX" ]; then
    echo "Index not provided. Creating new index 0..."
    INDEX=0
fi &&
echo "Creating temporary sub-directory..." &&
mkdir -p "$TUSTU_TEMP_DIR/$INDEX" &&

# Copy the necessary files to the temporary directory
echo "Copying files..." &&
{
# Add all git-tracked files
git ls-files;
echo ".dvc/config.local";
echo ".git";
} | while read file; do
    rsync -aR "$file" "$TUSTU_TEMP_DIR/$INDEX/"
done &&

# Change the working directory to the temporary sub-directory
cd $TUSTU_TEMP_DIR/$INDEX &&

# Set the DVC cache directory to the shared cache located in the host directory
echo "Setting DVC cache directory..." &&
dvc cache dir $DEFAULT_DIR/.dvc/cache &&

# Pull the data from the DVC remote repository
echo "Pulling data with DVC..." &&
dvc pull data/raw &&

# Run the experiment with passed parameters. Runs with the default parameters if none are passed.
echo "Running experiment..." &&
dvc exp run $EXP_PARAMS &&

# Push the results to the DVC remote repository
echo "Pushing experiment..." &&
dvc exp push origin &&

# Clean up the temporary sub-directory
echo "Cleaning up..." &&
cd .. &&
rm -rf $INDEX