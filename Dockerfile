# Starting from the PostgreSQL 15 image
FROM postgres:15

# Set working directory
WORKDIR /app

# Install Python and pip
RUN apt-get update && apt-get install -y python3.9 python3-pip python3-venv

# Create a virtual environment and activate it
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies (both PostgreSQL server and client)
RUN apt-get update && apt-get install -y git build-essential postgresql-server-dev-all

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

# Create the directory for pg_hba.conf
RUN mkdir -p /etc/postgresql/15/main
RUN echo "local all postgres md5" > /etc/postgresql/15/main/pg_hba.conf
RUN echo "host all postgres 127.0.0.1/32 md5" >> /etc/postgresql/15/main/pg_hba.conf
RUN echo "host all postgres ::1/128 md5" >> /etc/postgresql/15/main/pg_hba.conf

# Expose ports
EXPOSE 8888
EXPOSE 5432
