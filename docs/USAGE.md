**Usage:**
- Folder structure
- How to start experiments on cluster (two ways, sbatch slurm_job.sh or with editing the python script multi_submission.py to start multiple experiments at once for example with multiple experiments)
: Be cautious with it, set a limit. to not over occupy the cluster
- How to workflow back and forth. 
- 
- add new params, push and pull (debug locally without slurm job, For quick fixes on the cluster e.g. , use vim, nano or a code editor extension, like vs code remote ssh extension (not always reliable, but sometimes it works nicely))
- How to pull all experiments
- Monitoring with tensorboard live metrics via tensorboard host or your own computer (required rsync script)  
- How to check the slurm logs and job status
