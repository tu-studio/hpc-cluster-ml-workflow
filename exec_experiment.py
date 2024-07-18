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

# def submit_batch_job(params):
#     subprocess.call(["export", "EXP_PARAMS=--set-param", f"train.n_est={n_est}", "--set-param", f"train.min_split={min_split}"])
#     subprocess.call(["sbatch", "batchscript.sh"])


# Automated grid search experiments
test_split_list = [0.2, 0.3]
batch_size_list = [2048, 4096]

# Iterate over all combinations of hyperparameter values.
for test_split, batch_size in itertools.product(test_split_list, batch_size_list):
    # TODO: Funktion die default Batchscript nimmt in tmp ordner kopiert und flags "--set-param", f"train.n_est={n_est}", "--set-param", f"train.min_split={min_split}" added 
    # entweder default params
    # oder mit veränderung

    # Export the experiment parameters as an environment variable and submit the batch job in same shell to have access to the environment variable.
    command = f"export EXP_PARAMS='-S preprocess.test_split={test_split} -S train.batchsize={batch_size}' && sbatch batchjob.sh"
    subprocess.call(command, shell=True)

    
# 2. 
