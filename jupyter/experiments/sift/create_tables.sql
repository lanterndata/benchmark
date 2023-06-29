CREATE TABLE IF NOT EXISTS sift_base10k (
  id SERIAL PRIMARY KEY,
  v VECTOR(128)
);

\COPY sift_base10k (v) FROM '/jupyter/data/sift/sift_base10k.csv' WITH csv;

CREATE TABLE IF NOT EXISTS sift_base1m (
  id SERIAL PRIMARY KEY,
  v VECTOR(128)
);

\COPY sift_base1m (v) FROM '/jupyter/data/sift/sift_base1m.csv' WITH csv;

CREATE TABLE IF NOT EXISTS gist_base1m (
  id SERIAL PRIMARY KEY,
  v VECTOR(960)
);

\COPY gist_base1m (v) FROM '/jupyter/data/sift/gist_base1m.csv' WITH csv;

CREATE TABLE IF NOT EXISTS sift_base1b (
  id SERIAL PRIMARY KEY,
  v VECTOR(128)
);

\COPY sift_base1b (v) FROM '/jupyter/data/sift/sift_base1b.csv' WITH csv;