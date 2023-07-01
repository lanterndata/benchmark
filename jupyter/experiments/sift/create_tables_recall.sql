CREATE TABLE IF NOT EXISTS sift_query10k (
  id SERIAL PRIMARY KEY,
  v VECTOR(128)
);

\COPY sift_query10k (v) FROM '/Users/diqi/postvec/benchmark/jupyter/data/sift/siftsmall_query.csv' WITH csv;

CREATE TABLE IF NOT EXISTS sift_query1m (
  id SERIAL PRIMARY KEY,
  v VECTOR(128)
);

\COPY sift_query1m (v) FROM '/Users/diqi/postvec/benchmark/jupyter/data/sift/sift_query.csv' WITH csv;

CREATE TABLE IF NOT EXISTS sift_truth10k (
  id SERIAL PRIMARY KEY,
  indices INTEGER[]
);

\COPY sift_truth10k (indices) FROM '/Users/diqi/postvec/benchmark/jupyter/data/sift/siftsmall_groundtruth.csv' WITH csv;

CREATE TABLE IF NOT EXISTS sift_truth1m (
  id SERIAL PRIMARY KEY,
  indices INTEGER[]
);

\COPY sift_truth1m (indices) FROM '/Users/diqi/postvec/benchmark/jupyter/data/sift/sift_groundtruth.csv' WITH csv;