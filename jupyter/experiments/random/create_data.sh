N=$1

cat << EOF
  DROP TABLE IF EXISTS test_table2;

  CREATE TABLE test_table2 IF NOT EXISTS (
    id SERIAL PRIMARY KEY,
    vector5 VECTOR NOT NULL,
    vector10 VECTOR NOT NULL,
    vector50 VECTOR NOT NULL,
    vector100 VECTOR NOT NULL,
    vector200 VECTOR NOT NULL,
    vector400 VECTOR NOT NULL,
    vector600 VECTOR NOT NULL,
    vector800 VECTOR NOT NULL,
    vector1000 VECTOR NOT NULL
  );

  INSERT INTO test_table2 (
    vector5,
    vector10,
    vector50,
    vector100,
    vector200,
    vector400,
    vector600,
    vector800,
    vector1000
  )
  SELECT
    random_vector(5),
    random_vector(10),
    random_vector(50),
    random_vector(100),
    random_vector(200),
    random_vector(400),
    random_vector(600),
    random_vector(800),
    random_vector(1000)
  FROM
    generate_series(1, ${N});
EOF