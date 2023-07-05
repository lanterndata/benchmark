DROP TABLE IF EXISTS sift_query10k;
DROP TABLE IF EXISTS sift_query1m;
DROP TABLE IF EXISTS gist_query1m;
DROP TABLE IF EXISTS sift_truth10k;
DROP TABLE IF EXISTS sift_truth1m;
DROP TABLE IF EXISTS gist_truth1m;

CREATE TABLE IF NOT EXISTS sift_query10k (
  id SERIAL PRIMARY KEY,
  v VECTOR(128)
);

\COPY sift_query10k (v) FROM '/app/data/sift/siftsmall_query.csv' WITH csv;

CREATE TABLE IF NOT EXISTS sift_query1m (
  id SERIAL PRIMARY KEY,
  v VECTOR(128)
);

\COPY sift_query1m (v) FROM '/app/data/sift/sift_query.csv' WITH csv;

CREATE TABLE IF NOT EXISTS sift_truth10k (
  id SERIAL PRIMARY KEY,
  indices INTEGER[]
);

\COPY sift_truth10k (indices) FROM '/app/data/sift/siftsmall_groundtruth.csv' WITH csv;

CREATE TABLE IF NOT EXISTS sift_truth1m (
  id SERIAL PRIMARY KEY,
  indices INTEGER[]
);

\COPY sift_truth1m (indices) FROM '/app/data/sift/sift_groundtruth.csv' WITH csv;

CREATE TABLE IF NOT EXISTS gist_query1m (
  id SERIAL PRIMARY KEY,
  v VECTOR(960)
);

\COPY gist_query1m (v) FROM '/app/data/gist/gist_query.csv' WITH csv;

CREATE TABLE IF NOT EXISTS gist_truth1m (
  id SERIAL PRIMARY KEY,
  indices INTEGER[]
);

\COPY gist_truth1m (indices) FROM '/app/data/gist/gist_groundtruth.csv' WITH csv;