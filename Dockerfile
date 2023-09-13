# Starting from the PostgreSQL 15 image
FROM postgres:15

# Set working directory
WORKDIR /app

# Install Python, pip, and other dependencies
RUN apt-get update && apt-get install -y python3.11 python3-pip procps cmake wget git build-essential postgresql-server-dev-all curl

# Copy over the Python dependencies and install them
COPY core/requirements.txt /app/core/requirements.txt
COPY notebooks/requirements.txt /app/notebooks/requirements.txt
RUN pip install --no-cache-dir -r /app/core/requirements.txt --break-system-packages && \
    pip install --no-cache-dir -r /app/notebooks/requirements.txt --break-system-packages

# Add external index support
RUN \
    # Install ONNX Runtime
    mkdir -p /usr/local/lib && \
    cd /usr/local/lib && \
    wget https://github.com/microsoft/onnxruntime/releases/download/v1.15.1/onnxruntime-linux-x64-1.15.1.tgz && \
    tar xzf ./onnx*.tgz && \
    rm -rf ./onnx*.tgz && \
    mv ./onnx* ./onnxruntime && \
    apt install -y --no-install-recommends lsb-release wget build-essential ca-certificates zlib1g-dev pkg-config libreadline-dev clang curl gnupg libssl-dev jq && \
    # Install Rust
    curl -k -o /tmp/rustup.sh https://sh.rustup.rs && \
    chmod +x /tmp/rustup.sh && \
    /tmp/rustup.sh -y && \
    . "$HOME/.cargo/env" && \
    # Setup cargo deps
    cd /app && \
    mkdir .cargo && \
    echo "[target.$(rustc -vV | sed -n 's|host: ||p')]" >> .cargo/config && \
    echo 'rustflags = ["-C", "link-args=-Wl,-rpath,/usr/local/lib/onnxruntime/lib"]' >> .cargo/config && \
    cargo install cargo-pgrx --version 0.9.7 && \
    cargo pgrx init --pg15 /usr/bin/pg_config && \
    # Install package
    git clone https://github.com/lanterndata/lanterndb_extras.git && \
    cd lanterndb_extras && \
    cargo build -p lanterndb_create_index && cargo install --path lanterndb_create_index

# Install Postgres extensions
COPY extensions/ /app/extensions/
RUN chmod +x /app/extensions/* && \
    /app/extensions/install_pgvector.sh && \
    /app/extensions/install_lantern.sh && \
    /app/extensions/install_neon.sh

# Expose ports
EXPOSE 8888
EXPOSE 5432
