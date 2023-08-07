DROP TABLE experiment_results;
CREATE TABLE experiment_results (
  id SERIAL PRIMARY KEY,
  database TEXT NOT NULL,
  dataset TEXT NOT NULL,
  n INTEGER NOT NULL,
  k INTEGER NOT NULL DEFAULT 0,
  out TEXT,
  err TEXT,
  metric_type TEXT NOT NULL,
  metric_value DOUBLE PRECISION NOT NULL,
  CONSTRAINT unique_result UNIQUE (metric_type, "database", dataset, n, k)
);