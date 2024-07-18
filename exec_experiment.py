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

    # Automated grid search experiments
    n_est_values = [250, 300, 350, 400, 450, 500]
    min_split_values = [8, 16, 32, 64, 128, 256]

    # Iterate over all combinations of hyperparameter values.
    for n_est, min_split in itertools.product(n_est_values, min_split_values):
        # TODO: Funktion die default Batchscript nimmt in tmp ordner kopiert und flags "--set-param", f"train.n_est={n_est}", "--set-param", f"train.min_split={min_split}" added 
        # entweder default params
        submit_batch_job()
        # oder mit veränderung
        submit_batch_job(params={"n_est": n_est, "min_split": min_split})

def submit_batch_job:
    subprocess.call(["export", "EXP_PARAMS=--set-param", f"train.n_est={n_est}", "--set-param", f"train.min_split={min_split}"])
    subprocess.call(["sbatch", "batchscript.sh"])
# 2. 