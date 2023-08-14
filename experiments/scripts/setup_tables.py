import os
import argparse
import urllib.request
import psycopg2

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--datapath", default="/app/data",
                    help="Path to data directory")
args = parser.parse_args()


conn = psycopg2.connect(os.environ["DATABASE_URL"])
cur = conn.cursor()


def table_exists(schema, table):
    """Check if a table exists in the database."""
    try:
        with conn.cursor() as cur:
            cur.execute("""
            SELECT EXISTS (
                SELECT 1 
                FROM
                    information_schema.tables
                WHERE
                    table_schema = %s
                    AND table_name = %s
            );
            """, (schema, table))
            exists = cur.fetchone()[0]
            return exists
    except Exception as e:
        print(f"Error checking if table {table} exists: {e}")
        return False


def has_rows(schema, table):
    """Check if the table has non-zero rows."""
    if not table_exists(schema, table):
        print(f"Table {schema}.{table} does not exist.")
        return False
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {schema}.{table};")
            count = cur.fetchone()[0]
            return count > 0
    except Exception as e:
        print(f"Error checking row count for table {schema}.{table}: {e}")
        return False


def create_table(schema, name, vector_size):
    table_name = f"{schema}.{name}"
    if schema == 'public':
        sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id SERIAL PRIMARY KEY,
                indices INTEGER[]
            );
        """
    elif schema == 'real':
        sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id SERIAL PRIMARY KEY,
                v REAL[{vector_size}]
            );
        """
    elif schema == 'vector':
        sql = f"""
            CREATE EXTENSION IF NOT EXISTS vector SCHEMA vector;
            CREATE TABLE IF NOT EXISTS {table_name} (
                id SERIAL PRIMARY KEY,
                v vector.VECTOR({vector_size})
            );
        """
    else:
        raise ValueError(f"Invalid schema {schema}")
    with conn.cursor() as cur:
        cur.execute(sql)
        conn.commit()
    return table_name


def insert_table(dest_table, source_csv):
    with conn.cursor() as cur:
        with open(source_csv, 'r') as f:
            if 'truth' in dest_table:
                sql = f"COPY {dest_table} (indices) FROM '{source_csv}' WITH csv"
            else:
                sql = f"COPY {dest_table} (v) FROM '{source_csv}' WITH csv"
            cur.copy_expert(sql, f)
    conn.commit()


SCHEMAS = ['vector', 'real']

# Create schemas if they don't exist

with conn.cursor() as cur:
    for schema in SCHEMAS:
        cur.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
    conn.commit()

# Create tables if they don't exist

TABLES = [
    [128, "sift_base10k"],
    [128, "sift_query10k"],
    [128, "sift_truth10k"],

    [128, "sift_base1m"],
    [128, "sift_query1m"],
    [128, "sift_truth1m"],

    # [128, "sift_base1b"],
    [128, "sift_query1b"],
    [128, "sift_truth2m"],
    [128, "sift_truth5m"],
    [128, "sift_truth10m"],
    [128, "sift_truth20m"],
    [128, "sift_truth50m"],
    [128, "sift_truth100m"],
    [128, "sift_truth200m"],
    [128, "sift_truth500m"],

    [960, "gist_base1m"],
    [960, "gist_query1m"],
    [960, "gist_truth1m"],
]


def create_or_download_table(schema, vector_size, name):
    table_name = create_table(schema, name, vector_size)
    if not has_rows(schema, name):
        source_file = os.path.join(args.datapath, f"{name}.csv")
        if not os.path.exists(source_file):
            print(f"Source file {source_file} does not exist. Downloading...")
            if not os.path.exists(args.datapath):
                os.makedirs(args.datapath)
            urllib.request.urlretrieve(
                f"https://storage.googleapis.com/lanterndata/datasets/{source_file}", source_file)
            print("Download complete.")
        insert_table(table_name, source_file)
        print(f"Inserted data into {table_name}")
    else:
        print(f"Table {table_name} already exists. Skipping.")


def create_vector_table(vector_size, name):
    table_name = create_table('vector', name, vector_size)
    if not has_rows('vector', name):
        sql = f"""
            INSERT INTO {table_name} (id, v)
            SELECT id, v FROM real.{name};
        """
        with conn.cursor() as cur:
            cur.execute(sql)
            conn.commit()
        print(f"Inserted data into {table_name}")
    else:
        print(f"Table {table_name} already exists. Skipping.")


for vector_size, name in TABLES:
    if 'truth' in name:
        create_or_download_table('public', vector_size, name)
    else:
        create_or_download_table('real', vector_size, name)
        create_vector_table(vector_size, name)

# Create experiment results table if it doesn't exist

with conn.cursor() as cur:
    sql = """
        CREATE TABLE IF NOT EXISTS experiment_results (
            id SERIAL PRIMARY KEY,
            database TEXT NOT NULL,
            database_params TEXT NOT NULL,
            dataset TEXT NOT NULL,
            n INTEGER NOT NULL,
            k INTEGER NOT NULL DEFAULT 0,
            out TEXT,
            err TEXT,
            metric_type TEXT NOT NULL,
            metric_value DOUBLE PRECISION NOT NULL,
            CONSTRAINT unique_result UNIQUE (metric_type, database_params, database, dataset, n, k)
        );
    """
    cur.execute(sql)
    conn.commit()

cur.close()
conn.close()

print("Done!")
