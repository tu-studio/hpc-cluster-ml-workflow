# Copyright 2024 tu-studio
# This file is licensed under the Apache License, Version 2.0.
# See the LICENSE file in the root of this project for details.

import itertools
import subprocess
import os 

# Submit experiment for hyperparameter combination
def submit_batch_job(test_split, batch_size):
    # Set dynamic parameters for the batch job as environment variables
    # But dont forget to add the os.environ to the new environment variables otherwise the PATH is not found
    env = {
        **os.environ,
        "EXP_PARAMS": f"-S preprocess.test_split={test_split} -S train.batch_size={batch_size}"
    }
    # Run sbatch command with the environment variables as bash! subprocess! command (otherwise module not found)
    subprocess.run(['/usr/bin/bash', '-c', 'sbatch slurm_job.sh'], env=env)

if __name__ == "__main__":
    test_split_list = [0.2, 0.3]
    batch_size_list = [2048, 4096]
    # Iterate over a cartesian product parameter grid of the test_split and batch_size lists
    for test_split, batch_size in itertools.product(test_split_list, batch_size_list):
        submit_batch_job(test_split,batch_size)
