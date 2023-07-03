DROP TABLE IF EXISTS random_table_2m;

CREATE TABLE IF NOT EXISTS random_table_2m (
  id SERIAL PRIMARY KEY,
  vector5 VECTOR(5) NOT NULL,
  vector25 VECTOR(25) NOT NULL,
  vector125 VECTOR(125) NOT NULL,
  vector250 VECTOR(250) NOT NULL
);

INSERT INTO random_table_2m (
  vector5,
  vector25,
  vector125,
  vector250
)
SELECT
  random_vector(5),
  random_vector(25),
  random_vector(125),
  random_vector(250)
FROM
  generate_series(1, 2000000);

CREATE TABLE IF NOT EXISTS random_table_250k (
  id SERIAL PRIMARY KEY,
  vector5 VECTOR(5) NOT NULL,
  vector25 VECTOR(25) NOT NULL,
  vector125 VECTOR(125) NOT NULL,
  vector250 VECTOR(250) NOT NULL
);

CREATE TABLE IF NOT EXISTS random_table_500k (
  id SERIAL PRIMARY KEY,
  vector5 VECTOR(5) NOT NULL,
  vector25 VECTOR(25) NOT NULL,
  vector125 VECTOR(125) NOT NULL,
  vector250 VECTOR(250) NOT NULL
);

CREATE TABLE IF NOT EXISTS random_table_750k (
  id SERIAL PRIMARY KEY,
  vector5 VECTOR(5) NOT NULL,
  vector25 VECTOR(25) NOT NULL,
  vector125 VECTOR(125) NOT NULL,
  vector250 VECTOR(250) NOT NULL
);

CREATE TABLE IF NOT EXISTS random_table_1m (
  id SERIAL PRIMARY KEY,
  vector5 VECTOR(5) NOT NULL,
  vector25 VECTOR(25) NOT NULL,
  vector125 VECTOR(125) NOT NULL,
  vector250 VECTOR(250) NOT NULL
);

INSERT INTO random_table_1m
SELECT * FROM random_table_2m LIMIT 1000000;

INSERT INTO random_table_750k
SELECT * FROM random_table_2m LIMIT 750000;

INSERT INTO random_table_500k
SELECT * FROM random_table_2m LIMIT 500000;

INSERT INTO random_table_250k
SELECT * FROM random_table_2m LIMIT 250000;
