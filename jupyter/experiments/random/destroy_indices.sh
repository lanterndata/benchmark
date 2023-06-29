PGPASSWORD=postgres psql -d postgres -U postgres -h localhost -p 5432 << EOF
  DROP INDEX IF EXISTS vector5_index CASCADE;
  DROP INDEX IF EXISTS vector10_index CASCADE;
  DROP INDEX IF EXISTS vector50_index CASCADE;
  DROP INDEX IF EXISTS vector100_index CASCADE;
  DROP INDEX IF EXISTS vector200_index CASCADE;
  DROP INDEX IF EXISTS vector400_index CASCADE;
EOF

echo "Destroyed indices for test_table2"