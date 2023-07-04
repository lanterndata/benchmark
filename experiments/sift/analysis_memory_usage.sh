#!/bin/bash

N=$1

# Define log file paths
MEM_LOG="memory/${N}_mem.log"
TOP_LOG="memory/${N}_top.log"

# Remove log files if they exist
[ -f "$MEM_LOG" ] && rm "$MEM_LOG"
[ -f "$TOP_LOG" ] && rm "$TOP_LOG"

# Define the Postgres PID
POSTGRES_PID=1

# Echo PID for debugging
echo "Postgres PID: $POSTGRES_PID" >> "$MEM_LOG"

# Check if the PID is not empty
if [ -z "$POSTGRES_PID" ]; then
    echo "No Postgres PID found" >> "$MEM_LOG"
    exit 1
fi

# Start background process to monitor memory usage with 'top' command
top -b -p "$POSTGRES_PID" >> "$TOP_LOG" &

# Record the background process PID
PID_TOP=$!

# Echo monitoring PID for debugging
echo "Monitoring PID_TOP: $PID_TOP" >> "$MEM_LOG"

# Define index name
INDEX_NAME="sift_base${N}_index"

# Function to check completion status
check_completion_status() {
    local exit_code=$1
    local timestamp=$2
    
    if [ $exit_code -eq 0 ]; then
        echo -e "\n\n${timestamp}\n\n" >> "$TOP_LOG"
    else
        echo -e "\n\nFailed\n\n" >> "$TOP_LOG"
    fi
}

# Function to perform index deletion
perform_index_deletion() {
    sleep 1
    local current_timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    echo "DROP INDEX IF EXISTS $INDEX_NAME;" | psql -U postgres &
    local delete_index_pid=$!
    
    # Wait for the completion of index deletion
    wait $delete_index_pid
    local delete_index_exit_code=$?
    
    # Check the completion status
    local current_timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    check_completion_status $delete_index_exit_code "$current_timestamp | Index Deletion"
    sleep 1
}

# Function to perform index creation
perform_index_creation() {
    sleep 1
    local current_timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    echo -e "\n\n${current_timestamp} | Index Creation Started\n\n" >> "$TOP_LOG"
    echo "CREATE INDEX IF NOT EXISTS $INDEX_NAME ON sift_base${N} USING ivfflat (v vector_l2_ops) WITH (lists = 100);" | psql -U postgres &
    local create_index_pid=$!
    
    # Wait for the completion of index creation
    wait $create_index_pid
    local create_index_exit_code=$?
    
    # Check the completion status
    local current_timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    check_completion_status $create_index_exit_code "$current_timestamp | Index Creation Completed"
    sleep 1
}

# Run Postgres commands

# Index deletion
perform_index_deletion

# Index creation
perform_index_creation

# Index deletion
perform_index_deletion

# Once the Postgres command completes, terminate the background process
kill "$PID_TOP"
