FROM postgres:15

RUN apt-get update && apt-get install -y git build-essential postgresql-server-dev-all

RUN git clone https://github.com/pgvector/pgvector.git /pgvector

RUN cd /pgvector && make && make install