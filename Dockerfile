# Starting from the PostgreSQL 15 image
FROM postgres:15

# Set working directory
WORKDIR /app

# Install Python and pip
RUN apt-get update && apt-get install -y python3.11 python3-pip procps cmake wget

# Install dependencies (both PostgreSQL server and client)
RUN apt-get update && apt-get install -y git build-essential postgresql-server-dev-all

# Copy over the Python dependencies and install them
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt --break-system-packages

# Copy over the scripts to install Postgres extensions, and install them
COPY extensions/ /app/extensions/
RUN chmod +x /app/extensions/*
RUN /app/extensions/install_pgvector.sh
RUN /app/extensions/install_lantern.sh
RUN /app/extensions/install_neon.sh

# Expose ports
EXPOSE 8888
EXPOSE 5432
