#!/bin/bash
N=$1

PGPASSWORD=postgres psql -d postgres -U postgres -h localhost -p 5432 << EOF
  INSERT INTO test_table2 (
    vector5,
    vector10,
    vector50,
    vector100,
    vector200,
    vector400
  )
  SELECT
    random_vector(5),
    random_vector(10),
    random_vector(50),
    random_vector(100),
    random_vector(200),
    random_vector(400)
  FROM
    generate_series(1, ${N});
EOF

echo "Inserted $N rows into test_table2"