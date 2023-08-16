import os
import argparse
import urllib.request
from ..utils.database import DatabaseConnection
from ..utils.constants import Extension, EXTENSION_NAMES

# Set up an argument parser for command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--datapath", default="/app/data",
                    help="Path to data directory")
args = parser.parse_args()


def table_exists(extension, table):
    """Check if a table exists in the database."""
    try:
        sql = """
            SELECT EXISTS (
                SELECT 1 
                FROM
                    information_schema.tables
                WHERE
                    table_name = %s
            );
        """
        with DatabaseConnection(extension) as conn:
            exists = conn.select_one(sql, (table,))[0]
            return exists
    except Exception as e:
        print(f"Error checking if table {table} exists: {e}")
        return False


def has_rows(extension, table):
    """Check if the table has non-zero rows."""
    if not table_exists(table):
        print(f"Table {table} does not exist.")
        return False
    try:
        with DatabaseConnection(extension) as conn:
            count = conn.select_one(f"SELECT COUNT(*) FROM {table};")[0]
            return count > 0
    except Exception as e:
        print(f"Error checking row count for table {table}: {e}")
        return False


def create_table(extension, table_name, vector_size):
    """Creates a table based on the extension and table name."""
    if 'truth' in table_name:
        sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id SERIAL PRIMARY KEY,
                indices INTEGER[]
            );
        """
    elif extension == Extension.PGVECTOR or extension == Extension.NONE:
        sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id SERIAL PRIMARY KEY,
                v VECTOR({vector_size})
            );
        """
    else:
        sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id SERIAL PRIMARY KEY,
                v REAL[{vector_size}]
            );
        """
    with DatabaseConnection(extension) as conn:
        conn.execute(sql)


def insert_table(extension, dest_table, source_csv):
    """Inserts data from a CSV file into the specified table."""
    if 'truth' in dest_table:
        sql = f"COPY {dest_table} (indices) FROM '{source_csv}' WITH csv"
    else:
        sql = f"COPY {dest_table} (v) FROM '{source_csv}' WITH csv"
    with DatabaseConnection(extension) as conn:
        with open(source_csv, 'r') as f:
            conn.copy_expert(sql, f)


# List of tables and their corresponding vector sizes
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


def create_or_download_table(extension, vector_size, table_name):
    """
    Creates a table if it does not exist, and downloads and inserts data if the table 
    is empty. 
    """

    create_table(extension, table_name, vector_size)

    if not has_rows(extension, table_name):
        source_file = os.path.join(args.datapath, f"{table_name}.csv")
        if not os.path.exists(source_file):
            print(f"Source file {source_file} does not exist. Downloading...")
            if not os.path.exists(args.datapath):
                os.makedirs(args.datapath)
            urllib.request.urlretrieve(
                f"https://storage.googleapis.com/lanterndata/datasets/{table_name}.csv", source_file)
            print("Download complete.")

        insert_table(extension, table_name, source_file)

        print(f"Inserted data into {table_name}")

    else:
        print(f"Table {table_name} already exists. Skipping.")


# Creates the databases if they don't exist
for extension in Extension:
    with DatabaseConnection(autocommit=True) as conn:
        exists = conn.select_one(
            "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (extension.value,))
        if exists is None:
            conn.execute(f"CREATE DATABASE {extension.value};")
            print(f"Created database {extension.value}.")
        else:
            print(f"Database {extension.value} already exists. Skipping.")


# Enables the extensions if they are not already enabled
for extension, name in EXTENSION_NAMES.items():
    with DatabaseConnection(extension) as conn:
        conn.execute(f"CREATE EXTENSION IF NOT EXISTS {name};")
    print(f"Extension {name} is enabled.")


# Loop through each extension and table to ensure they are created and populated
for extension in Extension:
    for vector_size, table_name in TABLES:
        create_or_download_table(extension, vector_size, table_name)


# Connect to the database and create the experiment_results table if it doesn't exist
with DatabaseConnection() as conn:
    sql = """
        CREATE TABLE IF NOT EXISTS experiment_results (
            id SERIAL PRIMARY KEY,
            extension TEXT NOT NULL,
            index_params TEXT NOT NULL,
            dataset TEXT NOT NULL,
            n INTEGER NOT NULL,
            k INTEGER NOT NULL DEFAULT 0,
            out TEXT,
            err TEXT,
            metric_type TEXT NOT NULL,
            metric_value DOUBLE PRECISION NOT NULL,
            CONSTRAINT unique_result UNIQUE (metric_type, extension, index_params, dataset, n, k)
        );
    """
    conn.execute(sql)


print("Done!")
