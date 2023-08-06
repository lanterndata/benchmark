CREATE TABLE experiment_results (
  id SERIAL PRIMARY KEY,
  database TEXT NOT NULL,
  dataset TEXT NOT NULL,
  n INTEGER NOT NULL,
  k INTEGER,
  out TEXT,
  err TEXT,
  metric_type TEXT NOT NULL,
  metric_value DOUBLE PRECISION NOT NULL,
  CONSTRAINT unique_result UNIQUE NULLS NOT DISTINCT (metric_type, database, dataset, n, k)
);