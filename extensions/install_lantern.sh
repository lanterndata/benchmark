#!/bin/bash
set -e

# Clone or update lantern repository
export GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=no"
if [ -d "/lantern" ]; then
  echo "Updating lantern..."
  cd /lantern
  git fetch origin
  git pull
  git submodule update
else
  echo "Installing lantern..."
  git clone --recursive https://github.com/lanterndata/lanterndb.git /lantern
  cd /lantern
  mkdir build
fi

# Build lantern extension
cd build
cmake ..
make install