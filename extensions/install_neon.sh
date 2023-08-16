#!/bin/bash
set -e

# Clone or update neon repository
export GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=no"
if [ -d "/neon" ]; then
  echo "Updating neon..."
  cd /neon
  git fetch origin
  git pull
else
  echo "Installing neon..."
  git clone https://github.com/neondatabase/pg_embedding /neon
  cd /neon
fi

# Build neon extension
make
make install