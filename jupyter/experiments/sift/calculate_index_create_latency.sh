#!/bin/bash

# Set your database connection parameters
host="db"
port="5432"
user="postgres"
password="postgres"
database="postgres"

# You can specify N values as a space-separated list
N_values=("10k" "100k" "200k" "400k" "600k" "800k" "1m")

# Set your count
count=10

# Suppress client_min_messages
suppress_command="SET client_min_messages TO WARNING"

# Delete indices before running index experiments
./delete_indices.sh

# Loop over each N value
for N in "${N_values[@]}"
do
  # Loop count times
  for (( c=1; c<=$count; c++ ))
  do
    echo "Experiment - N: $N, count: $c"

    # Create and run your create index query
    create_index_query="CREATE INDEX sift_base${N}_index ON sift_base10k USING ivfflat (v vector_l2_ops) WITH (lists = 10)"
    PGPASSWORD=$password psql -h $host -p $port -U $user -d $database -c "$suppress_command" -c "\\timing" -c "$create_index_query"
    
    # Create and run your drop index query again
    PGPASSWORD=$password psql -h $host -p $port -U $user -d $database -c "$suppress_command" -c "$drop_index_query"
  done
done
