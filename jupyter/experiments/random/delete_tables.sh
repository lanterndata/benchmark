PGPASSWORD=postgres psql -d postgres -U postgres -h localhost -p 5432 -f - << EOF
  DROP TABLE IF EXISTS test_table2;
EOF