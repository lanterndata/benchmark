DROP TABLE IF EXISTS sift_base100k;
DROP TABLE IF EXISTS sift_base200k;
DROP TABLE IF EXISTS sift_base400k;
DROP TABLE IF EXISTS sift_base600k;
DROP TABLE IF EXISTS sift_base800k;
DROP TABLE IF EXISTS sift_base2m;
DROP TABLE IF EXISTS sift_base5m;
DROP TABLE IF EXISTS sift_base10m;
DROP TABLE IF EXISTS sift_base20m;
DROP TABLE IF EXISTS sift_base50m;
DROP TABLE IF EXISTS sift_base100m;
DROP TABLE IF EXISTS sift_base200m;
DROP TABLE IF EXISTS sift_base500m;

CREATE TABLE IF NOT EXISTS sift_base100k (
  id SERIAL PRIMARY KEY,
  v VECTOR(128)
);

CREATE TABLE IF NOT EXISTS sift_base200k (
  id SERIAL PRIMARY KEY,
  v VECTOR(128)
);

CREATE TABLE IF NOT EXISTS sift_base400k (
  id SERIAL PRIMARY KEY,
  v VECTOR(128)
);

CREATE TABLE IF NOT EXISTS sift_base600k (
  id SERIAL PRIMARY KEY,
  v VECTOR(128)
);

CREATE TABLE IF NOT EXISTS sift_base800k (
  id SERIAL PRIMARY KEY,
  v VECTOR(128)
);

CREATE TABLE IF NOT EXISTS sift_base2m (
  id SERIAL PRIMARY KEY,
  v VECTOR(128)
);

CREATE TABLE IF NOT EXISTS sift_base5m (
  id SERIAL PRIMARY KEY,
  v VECTOR(128)
);

CREATE TABLE IF NOT EXISTS sift_base10m (
  id SERIAL PRIMARY KEY,
  v VECTOR(128)
);

CREATE TABLE IF NOT EXISTS sift_base20m (
  id SERIAL PRIMARY KEY,
  v VECTOR(128)
);

CREATE TABLE IF NOT EXISTS sift_base50m (
  id SERIAL PRIMARY KEY,
  v VECTOR(128)
);

CREATE TABLE IF NOT EXISTS sift_base100m (
  id SERIAL PRIMARY KEY,
  v VECTOR(128)
);

CREATE TABLE IF NOT EXISTS sift_base200m (
  id SERIAL PRIMARY KEY,
  v VECTOR(128)
);

CREATE TABLE IF NOT EXISTS sift_base500m (
  id SERIAL PRIMARY KEY,
  v VECTOR(128)
);

DROP TABLE IF EXISTS gist_base100k;
DROP TABLE IF EXISTS gist_base200k;
DROP TABLE IF EXISTS gist_base400k;
DROP TABLE IF EXISTS gist_base600k;
DROP TABLE IF EXISTS gist_base800k;

CREATE TABLE IF NOT EXISTS gist_base100k (
  id SERIAL PRIMARY KEY,
  v VECTOR(960)
);

CREATE TABLE IF NOT EXISTS gist_base200k (
  id SERIAL PRIMARY KEY,
  v VECTOR(960)
);

CREATE TABLE IF NOT EXISTS gist_base400k (
  id SERIAL PRIMARY KEY,
  v VECTOR(960)
);

CREATE TABLE IF NOT EXISTS gist_base600k (
  id SERIAL PRIMARY KEY,
  v VECTOR(960)
);

CREATE TABLE IF NOT EXISTS gist_base800k (
  id SERIAL PRIMARY KEY,
  v VECTOR(960)
);

INSERT INTO sift_base100k
SELECT * FROM sift_base1m WHERE id <= 100000;

INSERT INTO sift_base200k
SELECT * FROM sift_base1m WHERE id <= 200000;

INSERT INTO sift_base400k
SELECT * FROM sift_base1m WHERE id <= 400000;

INSERT INTO sift_base600k
SELECT * FROM sift_base1m WHERE id <= 600000;

INSERT INTO sift_base800k
SELECT * FROM sift_base1m WHERE id <= 800000;
