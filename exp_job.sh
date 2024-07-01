#!/bin/bash

#  exp_job.sh
#  
#
#  Created by Michael Witte on 01.07.2024
#  

#SBATCH -J exp_job      

#SBATCH --ntasks=1                    
#SBATCH --nodes=1                     
#SBATCH --ntasks-per-core=1            
#SBATCH --cpus-per-task=4            
#SBATCH --gres=gpu:tesla:1            

#SBATCH --mem=100GB                  
#SBATCH --time=100:00:00            
#SBATCH --partition=gpu               

#SBATCH --mail-type=ALL
#SBATCH --mail-user={michael.gh.witte@campus.tu-berlin.de}

ulimit -u 512

## Source local Anaconda installation
source /home/users/m/motorik.michael/anaconda3/etc/profile.d/conda.sh

## Activate the conda environment
conda activate test_env

## Load cuda module 
module load nvidia/cuda/12.2

## Run Training
STORAGE_DEFAULT_DIRECTORY="$PWD/storage/" dvc exp run

if [ $? -ne 0 ]; then
    echo "Error occurred during DVC experiment run; exiting."
    exit 1
fi

dvc push

git add .
git commit -m "Update experiment"
git push

