from urllib.parse import urlparse
import subprocess
import os
import psycopg2
import csv
import argparse
import json
from tempfile import NamedTemporaryFile
from .number_utils import convert_string_to_number

# Allowed parameters

DEFAULT_INDEX_PARAMS = {
    'pgvector': {'lists': 100, 'probes': 1},
    'lantern': {'M': 2, 'ef_construction': 10, 'ef': 4}
}

VALID_INDEX_PARAMS = {index: list(default_params.keys())
                      for index, default_params in DEFAULT_INDEX_PARAMS.items()}

METRICS_WITH_K = ['select (latency ms)', 'select (tps)', 'recall']

METRICS_WITHOUT_N = ['insert (latency s)', 'insert bulk (latency s)']

VALID_METRICS = METRICS_WITH_K + METRICS_WITHOUT_N + \
    ['disk usage (bytes)', 'create (latency ms)']

VALID_EXTENSIONS = ['pgvector', 'lantern']

VALID_EXTENSIONS_AND_NONE = ['none'] + VALID_EXTENSIONS

VALID_DATASETS = {
    'sift': ['10k', '100k', '200k', '400k', '600k', '800k', '1m'],
    'gist': ['100k', '200k', '400k', '600k', '800k', '1m'],
}

VALID_QUERY_DATASETS = {
    'sift': ['10k', '1m'],
    'gist': ['1m'],
}

SUGGESTED_K_VALUES = [1, 3, 5, 10, 20, 40, 80]

# Argument parser


def parse_args(description, args):
    parser = argparse.ArgumentParser(description=description)

    if 'extension' in args:
        valid_extensions = VALID_EXTENSIONS_AND_NONE if 'none' in args else VALID_EXTENSIONS
        parser.add_argument('--extension', type=str,
                            choices=valid_extensions, required=True, help='Extension type')

    parser.add_argument("--dataset", type=str,
                        choices=VALID_DATASETS.keys(), required=True, help="Dataset name")

    if 'N' in args:
        parser.add_argument("--N", nargs='+', type=str,
                            required=True, help="dataset size")
    if 'K' in args:
        parser.add_argument("--K", nargs='+', type=int,
                            help="K values (e.g., 5)")

    if 'extension' in args:
        for index, valid_index_params in VALID_INDEX_PARAMS.items():
            for param in valid_index_params:
                parser.add_argument(
                    f"--{paran}", type=int, help=f"parameter for {index}")

    parsed_args = parser.parse_args()

    extension = parsed_args.extension if 'extension' in args else None
    dataset = parsed_args.dataset
    N_values = (
        parsed_args.N or VALID_DATASETS[dataset]) if 'N' in parsed_args else None
    K = (parsed_args.K or SUGGESTED_K_VALUES) if 'K' in parsed_args else None

    if 'N' in args:
        for N in N_values:
            if not N in VALID_DATASETS[dataset]:
                parser.error(
                    f"Invalid dataset size: {N_values}. Valid dataset sizes for {dataset} are: {', '.join(VALID_DATASETS[dataset])}")

    index_params = None
    if extension is not None:
        index_params = {key: getattr(parsed_args, key) for key in VALID_INDEX_PARAMS[extension] if getattr(
            parsed_args, key) is not None}

    return extension, index_params, dataset, N_values, K

# Parameters


def get_distinct_database_params(metric_type, extension, dataset, N):
    n_sql = '' if N is None else 'AND N = %s'
    sql = f"""
        SELECT DISTINCT
            database_params
        FROM
            experiment_results
        WHERE
            metric_type = %s
            AND database = %s
            AND dataset = %s
            {n_sql}
    """
    data = (metric_type, extension, dataset)
    if N is not None:
        data += (convert_string_to_number(N),)
    database_params = execute_sql(sql, data=data, select=True)
    database_params = [p[0] for p in database_params]
    return database_params


def get_experiment_results_for_params(metric_type, database, database_params, dataset, N):
    x_param = 'N' if N is None else 'K'
    n_sql = '' if N is None else 'AND N = %s'
    sql = f"""
        SELECT
            {x_param},
            metric_value
        FROM
            experiment_results
        WHERE
            metric_type = %s
            AND database = %s
            AND database_params = %s
            AND dataset = %s
            {n_sql}
        ORDER BY
            {x_param}
    """
    data = (metric_type, database, database_params, dataset)
    if N is not None:
        data += (convert_string_to_number(N),)
    results = execute_sql(sql, data=data, select=True)
    return results


def get_experiment_results(metric_type, extension, dataset, N=None):
    database_params = get_distinct_database_params(
        metric_type, extension, dataset, N)
    values = []
    for p in database_params:
        value = get_experiment_results_for_params(
            metric_type, extension, p, dataset, N)
        values.append((p, value))
    return values

# Get names


def get_table_name(dataset, N):
    if dataset not in VALID_DATASETS:
        raise Exception(
            f"Invalid dataset name = '{dataset}'. Valid dataset names are: {', '.join(VALID_DATASETS.keys())}")

    if N not in VALID_DATASETS[dataset]:
        raise Exception(
            f"Invalid N = '{N}'. Valid N values given dataset {dataset} are: {', '.join(VALID_DATASETS[dataset])}")

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
        print(sql)
        print()
        return False

    finally:
        if not cur_provided and cur is not None:
            cur.close()

        if not conn_provided and conn is not None:
            conn.close()

# Bash utils


def run_pgbench(query):
    db_connection_string = os.environ.get('DATABASE_URL')

    with NamedTemporaryFile(mode="w", delete=False) as tmp_file:
        tmp_file.write(query)
        tmp_file_path = tmp_file.name

    host, port, user, password, database = extract_connection_params(
        db_connection_string)
    command = f'PGPASSWORD={password} pgbench -d {database} -U {user} -h {host} -p {port} -f {tmp_file_path} -c 8 -j 8 -t 15 -r'
    stdout, stderr = run_command(command)
    return stdout, stderr


def run_command(command):
    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    return output.decode(), error.decode()

# Results


COLUMNS = ['database', 'database_params', 'dataset', 'n',
           'k', 'metric_type', 'metric_value', 'out', 'err']


def dump_results_to_csv():
    sql = f"SELECT {', '.join(COLUMNS[:-2])} FROM experiment_results ORDER BY metric_type, database, dataset"
    rows = execute_sql(sql, select=True)

    script_directory = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_directory, "../outputs/results.csv")

    with open(output_file, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(COLUMNS[:-2])
        for row in rows:
            csv_writer.writerow(row)


def save_result(metric_type, metric_value, database, database_params, dataset, n, k=0, out=None, err=None, conn=None, cur=None):
    columns = ', '.join(COLUMNS)
    placeholders = ', '.join(['%s'] * len(COLUMNS))
    updates = ', '.join(map(lambda col: f"{col} = EXCLUDED.{col}", COLUMNS))
    sql = f"INSERT INTO experiment_results ({columns}) VALUES ({placeholders}) ON CONFLICT ON CONSTRAINT unique_result DO UPDATE SET {updates}"
    data = (database, json.dumps(database_params), dataset,
            n, k, metric_type, metric_value, out, err)
    execute_sql(sql, data, conn=conn, cur=cur)
    dump_results_to_csv()
