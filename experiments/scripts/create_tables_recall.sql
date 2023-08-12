DROP TABLE IF EXISTS sift_query10k;
DROP TABLE IF EXISTS sift_query1m;
DROP TABLE IF EXISTS sift_query1b;
DROP TABLE IF EXISTS gist_query1m;
DROP TABLE IF EXISTS sift_truth10k;
DROP TABLE IF EXISTS sift_truth1m;
DROP TABLE IF EXISTS gist_truth1m;
DROP TABLE IF EXISTS sift_truth2m;
DROP TABLE IF EXISTS sift_truth5m;
DROP TABLE IF EXISTS sift_truth10m;
DROP TABLE IF EXISTS sift_truth20m;
DROP TABLE IF EXISTS sift_truth50m;
DROP TABLE IF EXISTS sift_truth100m;
DROP TABLE IF EXISTS sift_truth200m;
DROP TABLE IF EXISTS sift_truth500m;
DROP TABLE IF EXISTS sift_truth1b;

-- \set SIFTSMALL_PATH '/tmp/lanterndb/vector_datasets/siftsmall'
-- \set SIFT_PATH '/tmp/lanterndb/vector_datasets/sift'

CREATE TABLE IF NOT EXISTS sift_query10k (
  id SERIAL PRIMARY KEY,
  v VECTOR(128)
);

COPY sift_query10k (v) FROM '/tmp/lanterndb/vector_datasets/siftsmall/siftsmall_query.csv' WITH csv;

CREATE TABLE IF NOT EXISTS sift_query1m (
  id SERIAL PRIMARY KEY,
  v VECTOR(128)
);

COPY sift_query1m (v) FROM '/tmp/lanterndb/vector_datasets/sift/sift_query.csv' WITH csv;
-- I think the below is the name that some of the scripts expect this table to have...
CREATE TABLE IF NOT EXISTS sift_query100k (
  id SERIAL PRIMARY KEY,
  v VECTOR(128)
);
COPY sift_query100k (v) FROM '/tmp/lanterndb/vector_datasets/sift/sift_query.csv' WITH csv;

CREATE TABLE IF NOT EXISTS sift_truth10k (
  id SERIAL PRIMARY KEY,
  indices INTEGER[]
);

COPY sift_truth10k (indices) FROM '/tmp/lanterndb/vector_datasets/siftsmall/siftsmall_truth.csv' WITH csv;

CREATE TABLE IF NOT EXISTS sift_truth1m (
  id SERIAL PRIMARY KEY,
  indices INTEGER[]
);

COPY sift_truth1m (indices) FROM '/tmp/lanterndb/vector_datasets/sift/sift_truth.csv' WITH csv;

CREATE TABLE IF NOT EXISTS gist_query1m (
  id SERIAL PRIMARY KEY,
  v VECTOR(960)
);