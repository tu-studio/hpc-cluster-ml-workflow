#!/bin/bash

# Copyright 2024 tu-studio
# This file is licensed under the Apache License, Version 2.0.
# See the LICENSE file in the root of this project for details.

export $(grep -v '^#' global.env | xargs)

while true; do
    # Run the rsync command
    rsync -rv --inplace --progress $TUSTU_HPC_SSH:$TUSTU_HPC_DIR/$TUSTU_PROJECT_NAME/logs .
    
    # Wait for 30 seconds
    sleep 30
done