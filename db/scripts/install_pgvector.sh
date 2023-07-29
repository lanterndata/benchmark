#!/bin/bash
set -e

# Clone or update pgvector repository
export GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=no"
if [ -d "/pgvector" ]; then
  echo "Updating pgvector..."
  cd /pgvector
  git fetch origin
  git pull
else
  echo "Installing pgvector..."
  git clone https://github.com/pgvector/pgvector.git /pgvector
  cd /pgvector
fi

# Build pgvector extension
make
make install