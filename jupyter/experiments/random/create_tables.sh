#!/bin/bash
N=$1

PGPASSWORD=postgres psql -d postgres -U postgres -h localhost -p 5432 << EOF
  DROP TABLE IF EXISTS test_table2;

  CREATE TABLE IF NOT EXISTS test_table2 (
    id SERIAL PRIMARY KEY,
    vector5 VECTOR(5) NOT NULL,
    vector10 VECTOR(10) NOT NULL,
    vector50 VECTOR(50) NOT NULL,
    vector100 VECTOR(100) NOT NULL,
    vector200 VECTOR(200) NOT NULL,
    vector400 VECTOR(400) NOT NULL
  );
EOF

echo "Created test_table2"