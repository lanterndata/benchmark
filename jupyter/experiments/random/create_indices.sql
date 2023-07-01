CREATE INDEX random_table_2m_vector5_index ON random_table_2m USING ivfflat (vector5 vector_l2_ops) WITH (lists = 100);
CREATE INDEX random_table_2m_vector25_index ON random_table_2m USING ivfflat (vector25 vector_l2_ops) WITH (lists = 100);
CREATE INDEX random_table_2m_vector125_index ON random_table_2m USING ivfflat (vector125 vector_l2_ops) WITH (lists = 100);
CREATE INDEX random_table_2m_vector250_index ON random_table_2m USING ivfflat (vector250 vector_l2_ops) WITH (lists = 100);

CREATE INDEX random_table_1m_vector5_index ON random_table_1m USING ivfflat (vector5 vector_l2_ops) WITH (lists = 100);
CREATE INDEX random_table_1m_vector25_index ON random_table_1m USING ivfflat (vector25 vector_l2_ops) WITH (lists = 100);
CREATE INDEX random_table_1m_vector125_index ON random_table_1m USING ivfflat (vector125 vector_l2_ops) WITH (lists = 100);
CREATE INDEX random_table_1m_vector250_index ON random_table_1m USING ivfflat (vector250 vector_l2_ops) WITH (lists = 100);

CREATE INDEX random_table_750k_vector5_index ON random_table_750k USING ivfflat (vector5 vector_l2_ops) WITH (lists = 100);
CREATE INDEX random_table_750k_vector25_index ON random_table_750k USING ivfflat (vector25 vector_l2_ops) WITH (lists = 100);
CREATE INDEX random_table_750k_vector125_index ON random_table_750k USING ivfflat (vector125 vector_l2_ops) WITH (lists = 100);
CREATE INDEX random_table_750k_vector250_index ON random_table_750k USING ivfflat (vector250 vector_l2_ops) WITH (lists = 100);

CREATE INDEX random_table_500k_vector5_index ON random_table_500k USING ivfflat (vector5 vector_l2_ops) WITH (lists = 100);
CREATE INDEX random_table_500k_vector25_index ON random_table_500k USING ivfflat (vector25 vector_l2_ops) WITH (lists = 100);
CREATE INDEX random_table_500k_vector125_index ON random_table_500k USING ivfflat (vector125 vector_l2_ops) WITH (lists = 100);
CREATE INDEX random_table_500k_vector250_index ON random_table_500k USING ivfflat (vector250 vector_l2_ops) WITH (lists = 100);

CREATE INDEX random_table_250k_vector5_index ON random_table_250k USING ivfflat (vector5 vector_l2_ops) WITH (lists = 100);
CREATE INDEX random_table_250k_vector25_index ON random_table_250k USING ivfflat (vector25 vector_l2_ops) WITH (lists = 100);
CREATE INDEX random_table_250k_vector125_index ON random_table_250k USING ivfflat (vector125 vector_l2_ops) WITH (lists = 100);
CREATE INDEX random_table_250k_vector250_index ON random_table_250k USING ivfflat (vector250 vector_l2_ops) WITH (lists = 100);

