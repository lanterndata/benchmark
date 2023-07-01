#!/bin/bash

INDEXED=$1
N=$2
D=$3
K=$4
OUTPUT_FILE="outputs/${INDEXED}_N${N}_D${D}_K${K}.txt"

PGPASSWORD=postgres pgbench -d postgres -U postgres -h localhost -p 5432 -f - -c 5 -j 5 -t 10 -r > "$OUTPUT_FILE" 2>/dev/null << EOF
  \SET id random(1, 10000)

  SELECT * 
  FROM random_table_${N}
  ORDER BY vector${D} <-> (
    SELECT
      vector${D}
    FROM
      random_table_${N}
    WHERE
      id = :id
  ) 
  LIMIT ${K};
EOF

cat "$OUTPUT_FILE"
echo "Finished pgbench with indexed=$INDEXED, N=$N, D=$D, K=$K"