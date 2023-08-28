# Starting from the PostgreSQL 15 image
FROM postgres:15

# Set working directory
WORKDIR /app

# Install Python and pip
RUN apt-get update && apt-get install -y python3.11 python3-pip python3-venv procps cmake wget

# Create a virtual environment and activate it
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies (both PostgreSQL server and client)
RUN apt-get update && apt-get install -y git build-essential postgresql-server-dev-all

# Copy over the Python dependencies and install them
COPY ./experiments/requirements.txt /app/experiments/requirements.txt
RUN pip install --no-cache-dir -r /app/experiments/requirements.txt

# Create the directory for pg_hba.conf to enable access to DB
RUN mkdir -p /etc/postgresql/15/main
RUN echo "local all postgres md5" > /etc/postgresql/15/main/pg_hba.conf
RUN echo "host all postgres 127.0.0.1/32 md5" >> /etc/postgresql/15/main/pg_hba.conf
RUN echo "host all postgres ::1/128 md5" >> /etc/postgresql/15/main/pg_hba.conf

# Copy over the scripts to install Postgres extensions, and install them
COPY ./extensions/ /app/extensions/
RUN chmod +x /app/extensions/*
RUN /app/extensions/install_pgvector.sh
RUN /app/extensions/install_lantern.sh
RUN /app/extensions/install_neon.sh

# Expose ports
EXPOSE 8888
EXPOSE 5432
