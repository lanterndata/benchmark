#!/bin/bash

# Define the Postgres PID
POSTGRES_PID=$(pgrep -f postgres)

# Start background process to monitor memory usage
while true; do
  ps -p $POSTGRES_PID -o %mem,%cpu,cmd >> mem.log
  sleep 1
done &

# Record the background process PID
PID=$!

# Run your Postgres command here (this is just a placeholder)
echo "CREATE INDEX ..." | psql

# Once the Postgres command completes, terminate the background process
kill $PID