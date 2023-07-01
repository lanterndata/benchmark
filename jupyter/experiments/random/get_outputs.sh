#!/bin/bash

# Define values for N, K, D
K_values=(4 8 16 32 64)
N_values=("250k" "500k" "750k" "1m" "2m")
D_values=(5 25 125 250)

benchmark() {
  # Create index if needed
  should_index=$1
  if [ "$should_index" = "true" ]; then
    PGPASSWORD=postgres psql -d postgres -U postgres -h localhost -p 5432 -f ./create_indices.sql
  fi

  # Loop over N, D, K values and run pgbench
  for N in "${N_values[@]}"; do
    for D in "${D_values[@]}"; do
      for K in "${K_values[@]}"; do
        ./run_pgbench.sh "$should_index" "$N" "$D" "$K"
      done
    done
  done

  # Destroy indices
  if [ "$should_index" = "true" ]; then
    PGPASSWORD=postgres psql -d postgres -U postgres -h localhost -p 5432 -f ./delete_indices.sql
  fi
}

benchmark "false"
benchmark "true"