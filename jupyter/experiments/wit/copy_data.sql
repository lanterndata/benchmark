COPY tsv_data (
  language,
  page_url,
  image_url,
  page_title,
  section_title,
  hierarchical_section_title,
  caption_reference_description,
  caption_attribution_description,
  caption_alt_text_description,
  mime_type,
  original_height,
  original_width,
  is_main_image,
  attribution_passes_lang_id,
  page_changed_recently,
  context_page_description,
  context_section_description
) FROM '/jupyter/data/wit/data.tsv' DELIMITER E'\t' CSV HEADER;