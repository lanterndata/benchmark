DROP INDEX IF EXISTS sift_base10k_index CASCADE;
DROP INDEX IF EXISTS sift_base1m_index CASCADE;
DROP INDEX IF EXISTS gist_base1m_index CASCADE;
DROP INDEX IF EXISTS sift_base1b_index CASCADE;

CREATE INDEX sift_base10k_index ON sift_base10k USING ivfflat (v vector_l2_ops) WITH (lists = 100);
CREATE INDEX sift_base1m_index ON sift_base1m USING ivfflat (v vector_l2_ops) WITH (lists = 100);
CREATE INDEX gist_base1m_index ON gist_base1m USING ivfflat (v vector_l2_ops) WITH (lists = 100);
CREATE INDEX sift_base1b_index ON sift_base1b USING ivfflat (v vector_l2_ops) WITH (lists = 100);