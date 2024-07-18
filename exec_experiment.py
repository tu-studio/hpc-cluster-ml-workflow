# 0. Check that params.yaml is there
# 1. Make tmp folder if doesn't exis
# 2. Parse yaml file
# 3. For all param sets create a new timestamp / permutation if multiple lists exist
# 4. Creat exp folder with timestamp
# 5. Save specific params.yaml in folder
# 6. Add copy all other files except logs .dvc/cache, .dvc/tmp, docs and ...
# 7. Add symlink to logs
# 8. Submit batch job


#Example shell commands
timestamp=$(date +%s)
experiment_name="exp_$timestamp"

#TODO exclude dirs
rsync -Rr . tmp/$experiment_name
ln -s ./logs tmp/$experiment_name/logs
cd tmp/$experiment_name
# ./batchjob.sh