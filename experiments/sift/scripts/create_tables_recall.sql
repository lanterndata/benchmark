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

CREATE TABLE IF NOT EXISTS sift_query10k (
  id SERIAL PRIMARY KEY,
  v VECTOR(128)
);

\COPY sift_query10k (v) FROM '/app/data/siftsmall/siftsmall_query.csv' WITH csv;

CREATE TABLE IF NOT EXISTS sift_query1m (
  id SERIAL PRIMARY KEY,
  v VECTOR(128)
);

\COPY sift_query1m (v) FROM '/app/data/sift/sift_query.csv' WITH csv;

CREATE TABLE IF NOT EXISTS sift_truth10k (
  id SERIAL PRIMARY KEY,
  indices INTEGER[]
);

\COPY sift_truth10k (indices) FROM '/app/data/siftsmall/siftsmall_truth.csv' WITH csv;

CREATE TABLE IF NOT EXISTS sift_truth1m (
  id SERIAL PRIMARY KEY,
  indices INTEGER[]
);

\COPY sift_truth1m (indices) FROM '/app/data/sift/sift_truth.csv' WITH csv;

CREATE TABLE IF NOT EXISTS gist_query1m (
  id SERIAL PRIMARY KEY,
  v VECTOR(960)
);

\COPY gist_query1m (v) FROM '/app/data/gist/gist_query.csv' WITH csv;

CREATE TABLE IF NOT EXISTS gist_truth1m (
  id SERIAL PRIMARY KEY,
  indices INTEGER[]
);

\COPY gist_truth1m (indices) FROM '/app/data/gist/gist_truth.csv' WITH csv;

CREATE TABLE IF NOT EXISTS sift_query1b (
  id SERIAL PRIMARY KEY,
  v VECTOR(128)
);

\COPY sift_query1b (v) FROM '/app/data/siftbig/bigann_query.csv' WITH csv;

CREATE TABLE IF NOT EXISTS sift_truth2m (
  id SERIAL PRIMARY KEY,
  indices INTEGER[]
);

\COPY sift_truth2m (indices) FROM '/app/data/siftbig/gnd/idx_2M.csv' WITH csv;

CREATE TABLE IF NOT EXISTS sift_truth5m (
  id SERIAL PRIMARY KEY,
  indices INTEGER[]
);

\COPY sift_truth5m (indices) FROM '/app/data/siftbig/gnd/idx_5M.csv' WITH csv;

CREATE TABLE IF NOT EXISTS sift_truth10m (
  id SERIAL PRIMARY KEY,
  indices INTEGER[]
);

\COPY sift_truth10m (indices) FROM '/app/data/siftbig/gnd/idx_10M.csv' WITH csv;

CREATE TABLE IF NOT EXISTS sift_truth20m (
  id SERIAL PRIMARY KEY,
  indices INTEGER[]
);

\COPY sift_truth20m (indices) FROM '/app/data/siftbig/gnd/idx_20M.csv' WITH csv;

CREATE TABLE IF NOT EXISTS sift_truth50m (
  id SERIAL PRIMARY KEY,
  indices INTEGER[]
);

\COPY sift_truth50m (indices) FROM '/app/data/siftbig/gnd/idx_50M.csv' WITH csv;

CREATE TABLE IF NOT EXISTS sift_truth100m (
  id SERIAL PRIMARY KEY,
  indices INTEGER[]
);

\COPY sift_truth100m (indices) FROM '/app/data/siftbig/gnd/idx_100M.csv' WITH csv;

CREATE TABLE IF NOT EXISTS sift_truth200m (
  id SERIAL PRIMARY KEY,
  indices INTEGER[]
);

\COPY sift_truth200m (indices) FROM '/app/data/siftbig/gnd/idx_200M.csv' WITH csv;

CREATE TABLE IF NOT EXISTS sift_truth500m (
  id SERIAL PRIMARY KEY,
  indices INTEGER[]
);

\COPY sift_truth500m (indices) FROM '/app/data/siftbig/gnd/idx_500M.csv' WITH csv;

CREATE TABLE IF NOT EXISTS sift_truth1b (
  id SERIAL PRIMARY KEY,
  indices INTEGER[]
);

\COPY sift_truth1b (indices) FROM '/app/data/siftbig/gnd/idx_1000M.csv' WITH csv;