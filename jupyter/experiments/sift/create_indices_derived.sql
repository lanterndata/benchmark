CREATE INDEX IF NOT EXISTS sift_base100k_index ON sift_base100k USING ivfflat (v vector_l2_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS sift_base200k_index ON sift_base200k USING ivfflat (v vector_l2_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS sift_base400k_index ON sift_base400k USING ivfflat (v vector_l2_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS sift_base600k_index ON sift_base600k USING ivfflat (v vector_l2_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS sift_base800k_index ON sift_base800k USING ivfflat (v vector_l2_ops) WITH (lists = 100);