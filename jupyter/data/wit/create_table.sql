CREATE TABLE IF NOT EXISTS tsv_data (
  id SERIAL PRIMARY KEY,
  language TEXT,
  page_url TEXT,
  image_url TEXT,
  image_url_ai1 VECTOR(512),
  image_url_ai2 VECTOR(512),
  page_title TEXT,
  section_title TEXT,
  hierarchical_section_title TEXT,
  caption_reference_description TEXT,
  caption_attribution_description TEXT,
  caption_alt_text_description TEXT,
  mime_type TEXT,
  original_height INTEGER,
  original_width INTEGER,
  is_main_image BOOLEAN,
  attribution_passes_lang_id BOOLEAN,
  page_changed_recently BOOLEAN,
  context_page_description TEXT,
  context_page_description_ai1 VECTOR(768),
  context_page_description_ai2 VECTOR(768),
  context_section_description TEXT
);

CREATE INDEX ON tsv_data USING ivfflat (image_url_ai2 vector_l2_ops) WITH (lists = 100);
CREATE INDEX ON tsv_data USING ivfflat (context_page_description_ai2 vector_l2_ops) WITH (lists = 100);