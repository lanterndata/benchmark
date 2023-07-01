#!/bin/bash
INDEX=$1
N=$2
K=$3
OUTPUT_FILE="outputs/${INDEX}_${N}_K${K}.txt"

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
echo "Finished pgbench with N=$N, indexed=$INDEXED, K=$K"