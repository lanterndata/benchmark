PSQL_EXEC = psql -U postgres

jupyter:
	jupyter-lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password=''

psql:
	psql "$(DATABASE_URL)"
psql-none:
	psql "$(NONE_DATABASE_URL)"
psql-pgvector:
	psql "$(PGVECTOR_DATABASE_URL)"
psql-lantern:
	psql "$(LANTERN_DATABASE_URL)"
psql-neon:
	psql "$(NEON_DATABASE_URL)"