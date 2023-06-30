#!/bin/bash
INDEXED=$1
TABLE=$2
K=$3
OUTPUT_FILE="outputs/${INDEXED}_${T}_K${D}_K${K}.txt"

PGPASSWORD=postgres pgbench -d postgres -U postgres -h localhost -p 5432 -f - -c 5 -j 5 -t 15 -r > "$OUTPUT_FILE" 2>/dev/null << EOF
  \SET id random(1, 10000)

  SELECT *
  FROM ${TABLE}
  ORDER BY v <-> (
    SELECT
      v
    FROM
      ${TABLE}
    WHERE
      id = :id
  ) 
  LIMIT ${K};
EOF

cat "$OUTPUT_FILE"
echo "Finished pgbench with table=$TABLE, indexed=$INDEXED, K=$K"