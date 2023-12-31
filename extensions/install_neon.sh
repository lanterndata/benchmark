#!/bin/bash
set -e

# Clone or update neon repository
export GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=no"
if [ -d "/neon" ]; then
  echo "Updating neon..."
  cd /neon
  git fetch origin 0.3.6
  git pull
else
  echo "Installing neon..."
  git clone --branch 0.3.6 https://github.com/neondatabase/pg_embedding /neon
  cd /neon
fi

# Build neon extension
make
make install