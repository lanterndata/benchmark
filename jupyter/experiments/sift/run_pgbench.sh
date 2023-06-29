#!/bin/bash

INDEXED=$1
N=$2
D=$3
K=$4
OUTPUT_FILE="outputs/${INDEXED}_N${N}_D${D}_K${K}.txt"

PGPASSWORD=postgres pgbench -d postgres -U postgres -h localhost -p 5432 -f - -c 5 -j 5 -t 15 -r > "$OUTPUT_FILE" 2>/dev/null << EOF
  \set id random(1, ${N})

  SELECT * 
  FROM test_table2
  ORDER BY vector${D} <-> (
    SELECT
      vector${D}
    FROM
      test_table2
    WHERE
      id = :id
  ) 
  LIMIT ${K};
EOF

cat "$OUTPUT_FILE"
echo "Finished pgbench with indexed=$INDEXED, N=$N, D=$D, K=$K"