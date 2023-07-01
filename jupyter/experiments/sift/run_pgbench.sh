#!/bin/bash

# Define values for K, N
K_values=(4 8 16 32 64)
N_values=("10k" "100k" "200k" "400k" "600k" "800k" "1m")

benchmark() {
  PGPASSWORD=postgres psql -d postgres -U postgres -h localhost -p 5432 -f ./delete_indices.sql

  # Create index if needed
  should_index=$1
  if [ "$should_index" = "true" ]; then
    PGPASSWORD=postgres psql -d postgres -U postgres -h localhost -p 5432 -f ./create_indices.sql
    PGPASSWORD=postgres psql -d postgres -U postgres -h localhost -p 5432 -f ./create_indices_derived.sql
  fi

  # Loop over N, K values and run pgbench
  for N in "${N_values[@]}"; do
    for K in "${K_values[@]}"; do
      OUTPUT_FILE="outputs/${should_index}_${N}_K${K}.txt"

      PGPASSWORD=postgres pgbench -d postgres -U postgres -h localhost -p 5432 -f - -c 5 -j 5 -t 15 -r > "$OUTPUT_FILE" 2>/dev/null << EOF
  \SET id random(1, 10000)

  SELECT *
  FROM sift_base${N}
  ORDER BY v <-> (
    SELECT
      v
    FROM
      sift_base${N}
    WHERE
      id = :id
  ) 
  LIMIT ${K};
EOF

      cat "$OUTPUT_FILE"
      echo "Finished pgbench with N=$N, indexed=$should_index, K=$K"
    done
  done

  # Destroy indices
  if [ "$should_index" = "true" ]; then
    PGPASSWORD=postgres psql -d postgres -U postgres -h localhost -p 5432 -f ./delete_indices.sql
  fi
}

benchmark "false"
benchmark "true"
