# Starting from the Python image also includes a full Debian OS
FROM python:3.9

# Set working directory
WORKDIR /app

# Install dependencies (both PostgreSQL server and client)
RUN apt-get update && apt-get install -y git build-essential postgresql-15 postgresql-client-15 postgresql-server-dev-all

# Clone and install pgvector
RUN git clone https://github.com/pgvector/pgvector.git /pgvector
RUN cd /pgvector && make && make install

# Copy over the Python dependencies and install them
COPY ./requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy over the rest of the code
COPY ./data /app/data
COPY ./experiments /app/experiments
COPY ./db /app/db

# Expose ports
EXPOSE 8888
EXPOSE 5432

# Default command: start PostgreSQL
CMD service postgresql start && tail -f /dev/null
