DROP TABLE IF EXISTS sift_base10k;
DROP TABLE IF EXISTS sift_base1m;
DROP TABLE IF EXISTS gist_base1m;
DROP TABLE IF EXISTS sift_base1b;

CREATE TABLE IF NOT EXISTS sift_base10k (
  id SERIAL PRIMARY KEY,
  v VECTOR(128)
);

COPY sift_base10k (v) FROM '/tmp/lanterndb/vector_datasets/siftsmall/siftsmall_base.csv' WITH csv;

CREATE TABLE IF NOT EXISTS sift_base1m (
  id SERIAL PRIMARY KEY,
  v VECTOR(128)
);

COPY sift_base1m (v) FROM '/tmp/lanterndb/vector_datasets/sift/sift_base.csv' WITH csv;

-- CREATE TABLE IF NOT EXISTS gist_base1m (
--   id SERIAL PRIMARY KEY,
--   v VECTOR(960)
-- );

-- \COPY gist_base1m (v) FROM '/app/data/gist/gist_base.csv' WITH csv;

-- CREATE TABLE IF NOT EXISTS sift_base1b (
--   id SERIAL PRIMARY KEY,
--   v VECTOR(128)
-- );

-- \COPY sift_base1b (v) FROM '/app/data/siftbig/bigann_base.csv' WITH csv;