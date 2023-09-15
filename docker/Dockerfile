# Starting from the PostgreSQL 15 image
FROM postgres:15

# Set working directory
WORKDIR /app

# Install Python, pip, and other dependencies
RUN apt-get update && apt-get install -y python3.11 python3-pip procps cmake git build-essential postgresql-server-dev-15 openssh-client

# Copy over the Python dependencies and install them
COPY core/requirements.txt /app/core/requirements.txt
COPY notebooks/requirements.txt /app/notebooks/requirements.txt
RUN pip install --no-cache-dir -r /app/core/requirements.txt --break-system-packages && \
    pip install --no-cache-dir -r /app/notebooks/requirements.txt --break-system-packages

# Expose ports
EXPOSE 8888
