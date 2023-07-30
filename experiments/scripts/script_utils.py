import pickle
from urllib.parse import urlparse
import subprocess
import os
import psycopg2

# Allowed parameters

VALID_DATASETS = {
    'sift': ['10k', '100k', '200k', '400k', '600k', '800k', '1m'],
    'gist': ['100k', '200k', '400k', '600k', '800k', '1m'],
}

# Save / fetch pickled data

def save_data(file_name, data):
    with open(file_name, 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

def fetch_data(file_name):
    if not os.path.exists(file_name):
        raise FileNotFoundError(f"There is no experiment run for dataset")
    with open(file_name, 'rb') as handle:
        return pickle.load(handle)

# Print

def print_labels(title, *cols):
    print_row(title)
    print('-' * len(cols) * 10)
    print_row(*cols)
    print('-' * len(cols) * 10)

def print_row(*cols):
    row = ''.join([col.ljust(10) for col in cols])
    print(row)

# Get names

def get_table_name(dataset, N):
    if dataset not in VALID_DATASETS:
        raise Exception(f"Invalid dataset name. Valid dataset names are: {', '.join(VALID_DATASETS.keys())}")

    if N not in VALID_DATASETS[dataset]:
        raise Exception(f"Invalid N. Valid N values given dataset {dataset} are: {', '.join(VALID_DATASETS[dataset])}")
    
    return f"{dataset}_base{N}"

def get_index_name(dataset, N):
    return get_table_name(dataset, N) + "_index"

# Database utils

def extract_connection_params(db_url):
    parsed_url = urlparse(db_url)
    host = parsed_url.hostname
    port = parsed_url.port
    user = parsed_url.username
    password = parsed_url.password
    database = parsed_url.path.lstrip("/")

    return host, port, user, password, database

def execute_sql(sql, conn=None, cur=None):
    conn_provided = conn is not None
    cur_provided = cur is not None

    if not conn_provided:
        database_url = os.environ.get('DATABASE_URL')
        conn = psycopg2.connect(database_url)

    if not cur_provided:
        cur = conn.cursor()

    cur.execute(sql)
    conn.commit()

    if not cur_provided:
        cur.close()
    
    if not conn_provided:
        conn.close()

# Bash utils

def run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    return output.decode(), error.decode()