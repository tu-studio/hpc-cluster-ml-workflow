#!/bin/bash

load_env() {
  while IFS= read -r line; do
    if [ ! -z "$line" ]; then
      export "$line"
    fi
  done < "$1"
  echo "Environment variables set from $1."
}

if [ -f "global.env" ]; then
  load_env "global.env"
fi

