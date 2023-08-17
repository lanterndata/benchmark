DOCKER_EXEC = docker exec -it benchmark
PSQL_EXEC = $(DOCKER_EXEC) psql -U postgres

build:
	docker compose build

up:
	docker compose up

down:
	docker compose down

destroy:
	docker system prune --volumes -f

jupyter:
	$(DOCKER_EXEC) jupyter-lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password=''

bash:
	$(DOCKER_EXEC) bash

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