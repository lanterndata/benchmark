#!/bin/bash

# Define values for N, K, D
K_values=(1 2 4 8 16 32 64)
N_values=(100000 500000 1000000 5000000 10000000)
D_values=(5 10 50 100 200 400 800)

# Loop over p1 and p2 values
for N in "${N_values[@]}"; do
  ./create_data.sh "$N"
  for D in "${D_values[@]}"; do
    for K in "${K_values[@]}"; do
      ./run_pgbench.sh "$N" "$D" "$K"
      echo "Finished pgbench with N=$N, D=$D, K=$K"
    done
  done
  ./destroy_data.sh
done