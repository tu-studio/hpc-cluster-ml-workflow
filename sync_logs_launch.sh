#!/bin/bash

# Copyright 2024 tu-studio
# This file is licensed under the Apache License, Version 2.0.
# See the LICENSE file in the root of this project for details.

# Kills previous processes to ensure only one instance is running
pkill -f logs/sync_logs.sh

# Run the sync_logs.sh script in the background
./logs/sync_logs.sh > logs/local_rsync_output.log 2>&1 &