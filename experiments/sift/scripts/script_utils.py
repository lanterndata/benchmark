import pickle
from urllib.parse import urlparse
import subprocess
import os
import psycopg2

VALID_DATASETS = {
    'sift': ['10k', '100k', '200k', '400k', '600k', '800k', '1m'],
    'gist': ['10k', '100k', '200k', '400k', '600k', '800k', '1m'],
}

def save_data(file_name, data):
    with open(file_name, 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

def fetch_data(file_name):
    if not os.path.exists(file_name):
        raise FileNotFoundError(f"There is no experiment run for dataset")
    with open(file_name, 'rb') as handle:
        return pickle.load(handle)

def print_labels(dataset, *cols):
    print_row(dataset)
    print('-' * len(cols) * 10)
    print_row(*cols)
    print('-' * len(cols) * 10)

def print_row(*cols):
    row = ''.join([col.ljust(10) for col in cols])
    print(row)

def get_table_name(dataset, N):
    if dataset not in VALID_DATASETS:
        raise Exception(f"Invalid dataset name. Valid dataset names are: {', '.join(VALID_DATASETS.keys())}")

    if N not in VALID_DATASETS[dataset]:
        raise Exception(f"Invalid N. Valid N values given dataset {dataset} are: {', '.join(VALID_DATASETS[dataset])}")
    
    return f"{dataset}_base{N}"

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


def convert_string_to_number(s):
    s = s.strip().lower()  # remove spaces and convert to lowercase

    multiplier = 1  # default is 1
    if s.endswith('k'):
        multiplier = 10**3
        s = s[:-1]  # remove the last character
    elif s.endswith('m'):
        multiplier = 10**6
        s = s[:-1]
    elif s.endswith('b'):
        multiplier = 10**9
        s = s[:-1]

    try:
        return int(float(s) * multiplier)
    except ValueError:
        print(f"Could not convert {s} to a number.")
        return None

def convert_number_to_string(num):
    if num % 10**9 == 0:
        return str(int(num // 10**9)) + 'b'
    elif num % 10**6 == 0:
        return str(int(num // 10**6)) + 'm'
    elif num % 10**3 == 0:
        return str(int(num // 10**3)) + 'k'
    else:
        return str(int(num))

def convert_bytes_to_number(bytes):
    if 'kB' in bytes:
        return float(bytes.replace(' kB', '')) / 1024
    elif 'MB' in bytes:
        return float(bytes.replace(' MB', ''))
    else:
        return None
  
def extract_connection_params(db_url):
    parsed_url = urlparse(db_url)
    host = parsed_url.hostname
    port = parsed_url.port
    user = parsed_url.username
    password = parsed_url.password
    database = parsed_url.path.lstrip("/")

    return host, port, user, password, database

def run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    return output.decode(), error.decode()

# Lighter to darker shades of green
green_shades = [
    'rgb(153,255,153)', 
    'rgb(102,255,102)',  
    'rgb(51,255,51)',  
    'rgb(0,255,0)',
    'rgb(0,204,0)',  
    'rgb(0,153,0)',  
]

# Lighter to darker shades of green
red_shades = [
    'rgb(255,153,153)',  
    'rgb(255,102,102)',  
    'rgb(255,51,51)',  
    'rgb(255,0,0)',
    'rgb(204,0,0)',  
    'rgb(153,0,0)',
]