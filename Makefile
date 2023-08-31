PSQL_EXEC = psql -U postgres

jupyter:
	jupyter-lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password=''

psql:
	$(PSQL_EXEC)
psql-none:
	$(PSQL_EXEC) -d none
psql-pgvector:
	$(PSQL_EXEC) -d pgvector
psql-lantern:
	$(PSQL_EXEC) -d lantern
psql-neon:
	$(PSQL_EXEC) -d neon