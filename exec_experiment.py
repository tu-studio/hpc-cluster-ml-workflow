# 0. Check that params.yaml is there
# 1. Make tmp folder if doesn't exis
# 2. Parse yaml file
# 3. For all param sets create a new timestamp / permutation if multiple lists exist
# 4. Creat exp folder with timestamp
# 5. Save specific params.yaml in folder
# 6. Add copy all other files except logs .dvc/cache, .dvc/tmp, docs and ...
# 7. Add symlink to logs
# 8. Submit batch job

# 0. Params.yaml has default values
# 1. Change some values and add them to queue
    # Example
import itertools
import subprocess

# Submit experiment for hyperparameter combination
def submit_batch_job(test_split, batch_size):
    # Set dynamic parameters for the batch job as environment variable
    env = {'EXP_PARAMS': f'-S preprocess.test_split={test_split} -S train.batchsize={batch_size}'}
    # Run sbatch command with the environment variables as bash! subprocess! command (otherwise module not found)
    subprocess.run(['/usr/bin/bash', '-c', 'sbatch batchjob.sh'], env=env)

# Iterate over all combinations of hyperparameters
test_split_list = [0.2, 0.3]
batch_size_list = [2048, 4096]
for test_split, batch_size in itertools.product(test_split_list, batch_size_list):
    submit_batch_job(test_split, batch_size)
