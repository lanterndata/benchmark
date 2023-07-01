#!/bin/bash

# bash strict mode
set -euo pipefail
IFS=$'\n\t'

# Define values for K, N
K_values=(4 8 16 32 64)
N_values=("10k" "100k" "200k" "400k" "600k" "800k" "1m")

benchmark() {
  PGPASSWORD=postgres psql -d postgres -U postgres -h localhost -p 5432 -f ./delete_indices.sql

  # Create index if needed
  should_index=$1
  index=$2
  if [ "$should_index" = "true" ]; then
    PGPASSWORD=postgres psql -d postgres -U postgres -h localhost -p 5432 -f ./create_indices.sql -v index=$index
  fi

  # Loop over T, K values and run pgbench
  for N in "${N_values[@]}"; do
    for K in "${K_values[@]}"; do
      ./run_pgbench.sh "$should_index" "$index" "$N" "$K"
    done
  done

  # Destroy indices
  if [ "$should_index" = "true" ]; then
    PGPASSWORD=postgres psql -d postgres -U postgres -h localhost -p 5432 -f ./delete_indices.sql
  fi
}

benchmark "false"
benchmark "true" "ivfflat"
#benchmark "true" "hnsw"
