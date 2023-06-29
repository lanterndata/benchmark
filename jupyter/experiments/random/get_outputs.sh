#!/bin/bash

# Define values for N, K, D
K_values=(4 8 16 32 64)
N_values=(100000 200000 400000 600000 800000)
D_values=(5 10 50 100 200 400)

benchmark() {
  # Create tables
  ./create_tables.sh

  # Create index if needed
  should_index=$1
  if [ "$should_index" = "true" ]; then
    ./create_indices.sh
  fi

  # Loop over N, D, K values
  for i in "${!N_values[@]}"; do
    N="${N_values[$i]}"

    # Calculate delta based on current and previous N
    if (( i == 0 )); then
      delta="${N_values[0]}"
    else
      delta=$((N_values[i] - N_values[i - 1]))
    fi

    # Insert delta rows of data
    time ./insert_rows.sh "$delta"

    # Run pgbench
    for D in "${D_values[@]}"; do
      for K in "${K_values[@]}"; do
        ./run_pgbench.sh "$should_index" "$N" "$D" "$K"
      done
    done
  done

  # Destroy tables
  ./destroy_tables.sh
}

benchmark "false"
benchmark "true"