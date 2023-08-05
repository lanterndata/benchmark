import pickle
from urllib.parse import urlparse
import subprocess
import os
import psycopg2
import csv
from .number_utils import convert_number_to_string

# Allowed parameters

VALID_METRICS = ['select (latency ms)', 'select (tps)', 'recall', 'disk usage (bytes)']

METRICS_WITH_K = ['select (latency ms)', 'select (tps)', 'recall']

VALID_EXTENSIONS = ['none', 'pgvector', 'lantern']

VALID_DATASETS = {
    'sift': ['10k', '100k', '200k', '400k', '600k', '800k', '1m'],
    'gist': ['100k', '200k', '400k', '600k', '800k', '1m'],
}

VALID_QUERY_DATASETS = {
    'sift': ['10k', '1m'],
    'gist': ['1m'],
}

SUGGESTED_K_VALUES = [1, 3, 5, 10, 20, 40, 80]

# Get names

def get_table_name(dataset, N):
    if dataset not in VALID_DATASETS:
        raise Exception(f"Invalid dataset name = '{dataset}'. Valid dataset names are: {', '.join(VALID_DATASETS.keys())}")

    if N not in VALID_DATASETS[dataset]:
        raise Exception(f"Invalid N = '{N}'. Valid N values given dataset {dataset} are: {', '.join(VALID_DATASETS[dataset])}")
    
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

def execute_sql(sql, data=None, conn=None, cur=None, select=False, select_one=False):
    conn_provided = conn is not None
    cur_provided = cur is not None

    try:
        if not conn_provided:
            database_url = os.environ.get('DATABASE_URL')
            conn = psycopg2.connect(database_url)

        if not cur_provided:
            cur = conn.cursor()

        if data is None:
            cur.execute(sql)
        else:
            cur.execute(sql, data)
        
        if select:
            data = cur.fetchall()
            return data
        elif select_one:
            data = cur.fetchone()
            if data is not None:
              return data[0]
            return None
        else:
            conn.commit()
            return True

    except Exception as e:
      print("Error executing SQL:", e)
      return False

    finally:
        if not cur_provided and cur is not None:
            cur.close()
        
        if not conn_provided and conn is not None:
            conn.close()

# Bash utils

def run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    return output.decode(), error.decode()

# Results

COLUMNS = ['database', 'dataset', 'n', 'k', 'metric_type', 'metric_value', 'out', 'err']

def dump_results_to_csv():
    sql = f"SELECT {', '.join(COLUMNS[:-2])} FROM experiment_results ORDER BY metric_type, database, dataset"
    rows = execute_sql(sql, select=True)
    output_file = "outputs/results.csv"
    with open(output_file, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(COLUMNS[:-2])
        for row in rows:
            csv_writer.writerow(row)

def save_result(metric_type, metric_value, database, dataset, n, k=None, out=None, err=None, conn=None, cur=None):
    columns = ', '.join(COLUMNS)
    placeholders = ', '.join(['%s'] * len(COLUMNS))
    updates = ', '.join(map(lambda col: f"{col} = EXCLUDED.{col}", COLUMNS))
    sql = f"INSERT INTO experiment_results ({columns}) VALUES ({placeholders}) ON CONFLICT ON CONSTRAINT unique_result DO UPDATE SET {updates}"
    data = (database, dataset, n, k, metric_type, metric_value, out, err)
    execute_sql(sql, data, conn=conn, cur=cur)
    dump_results_to_csv()