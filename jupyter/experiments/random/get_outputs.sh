#!/bin/bash

# Define values for N, K, D
K_values=(2 4 8 16 32 64)
N_values=(100000 200000 400000 800000 1600000)
D_values=(5 10 50 100 200 400)

# Loop over N, D, K values
for N in "${N_values[@]}"; do
  ./create_data.sh "$N"
  for D in "${D_values[@]}"; do
    for K in "${K_values[@]}"; do
      ./run_pgbench.sh "$N" "$D" "$K"
    done
  done
  ./destroy_data.sh
done