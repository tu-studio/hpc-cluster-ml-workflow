#!/bin/bash

#SBATCH -J exp_job      

#SBATCH --ntasks=1                    
#SBATCH --nodes=1                     
#SBATCH --ntasks-per-core=1            
#SBATCH --cpus-per-task=1            
#SBATCH --gres=gpu:tesla:1            

#SBATCH --mem=100GB                  
#SBATCH --time=100:00:00            
#SBATCH --partition=gpu               

#SBATCH --mail-type=ALL
#SBATCH --mail-user={michael.gh.witte@campus.tu-berlin.de}

ulimit -u 512

## Load cuda module 
module load nvidia/cuda/12.2

module load singularity/4.0.2

singularity pull docker://michaelwitte/ml-pipeline-image:latest

STORAGE_DEFAULT_DIRECTORY="$PWD" singularity exec --bind $(pwd):/usr/src/app --bind $HOME/.ssh:/root/.ssh ml-pipeline-image_latest.sif sh -c "ssh-keyscan github.com >> /root/.ssh/known_hosts && git config --global user.name 'michaelwitte' && git config --global user.email 'michael-witte@hotmail.de' && dvc exp run"

## if [ $? -ne 0 ]; then
##    echo "Error occurred during DVC experiment run; exiting."
##    exit 1
## fi


