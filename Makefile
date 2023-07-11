DOCKER_EXEC = docker exec -it benchmark

build:
	docker compose build

up:
	docker compose up

down:
	docker compose down

destroy:
	docker system prune --volumes -f

bash:
	$(DOCKER_EXEC) bash

jupyter:
	$(DOCKER_EXEC) jupyter-lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password=''

psql:
	$(DOCKER_EXEC) psql -U postgres
