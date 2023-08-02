CREATE TABLE experiment_results (
  id SERIAL PRIMARY KEY,
  database TEXT NOT NULL,
  version TEXT,
  dataset TEXT NOT NULL,
  n INTEGER NOT NULL,
  k INTEGER,
  out TEXT,
  err TEXT,
  metric_type TEXT NOT NULL,
  metric_value DOUBLE PRECISION NOT NULL,
  UNIQUE(metric_type, database, dataset, n, k)
);