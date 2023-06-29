#!/bin/bash

# Define values for N, K, D
INDEX_values=(true false)
K_values=(4 8 16 32 64)
N_values=(100000 200000 400000 600000 800000)
D_values=(5 10 50 100 200 400)

# Loop over N, D, K values
for indexed in "${INDEX_values[@]}"; do
  for N in "${N_values[@]}"; do
    ./create_data.sh "$indexed" "$N"
    for D in "${D_values[@]}"; do
      for K in "${K_values[@]}"; do
        ./run_pgbench.sh "$indexed" "$N" "$D" "$K"
      done
    done
    ./destroy_data.sh
  done
done