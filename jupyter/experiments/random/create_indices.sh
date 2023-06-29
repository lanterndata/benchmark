#!/bin/bash

PGPASSWORD=postgres psql -d postgres -U postgres -h localhost -p 5432 << EOF
  CREATE INDEX vector5_index ON test_table2 USING ivfflat (vector5 vector_l2_ops) WITH (lists = 100);
  CREATE INDEX vector10_index ON test_table2 USING ivfflat (vector10 vector_l2_ops) WITH (lists = 100);
  CREATE INDEX vector50_index ON test_table2 USING ivfflat (vector50 vector_l2_ops) WITH (lists = 100);
  CREATE INDEX vector100_index ON test_table2 USING ivfflat (vector100 vector_l2_ops) WITH (lists = 100);
  CREATE INDEX vector200_index ON test_table2 USING ivfflat (vector200 vector_l2_ops) WITH (lists = 100);
  CREATE INDEX vector400_index ON test_table2 USING ivfflat (vector400 vector_l2_ops) WITH (lists = 100);
EOF

echo "Created indices for test_table2"