DOCKER_EXEC = docker exec -it benchmark

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
	$(DOCKER_EXEC) psql -U postgres -d experiments
psql-pgvector:
	$(DOCKER_EXEC) psql -U postgres -d pgvector
psql-lantern:
	$(DOCKER_EXEC) psql -U postgres -d lantern
psql-neon:
	$(DOCKER_EXEC) psql -U postgres -d neon