CREATE INDEX sift_base10k_index ON sift_base10k USING :index (v vector_l2_ops);
CREATE INDEX sift_base100k_index ON sift_base100k USING :index (v vector_l2_ops);
--CREATE INDEX sift_base200k_index ON sift_base200k USING :index (v vector_l2_ops);
--CREATE INDEX sift_base400k_index ON sift_base400k USING :index (v vector_l2_ops);
--CREATE INDEX sift_base600k_index ON sift_base600k USING :index (v vector_l2_ops);
-- CREATE INDEX sift_base800k_index ON sift_base800k USING :index (v vector_l2_ops);
-- CREATE INDEX sift_base1m_index ON sift_base1m USING :index (v vector_l2_ops);
-- CREATE INDEX gist_base1m_index ON gist_base1m USING ivfflat (v vector_l2_ops) WITH (lists = 100);
-- CREATE INDEX sift_base1b_index ON sift_base1b USING ivfflat (v vector_l2_ops) WITH (lists = 100);
