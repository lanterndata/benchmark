import os
import argparse
import urllib.request
from core.database import DatabaseConnection
from utils.constants import Extension, EXTENSION_NAMES, get_vector_dim


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
    if not table_exists(extension, table):
        print(f"Table {table} does not exist.")
        return False
    try:
        with DatabaseConnection(extension) as conn:
            count = conn.select_one(f"SELECT COUNT(*) FROM {table};")[0]
            return count > 0
    except Exception as e:
        print(f"Error checking row count for table {table}: {e}")
        return False


def get_create_table_query(extension, table_name):
    """Returns the SQL query to create a table."""
    if 'truth' in table_name:
        return f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id SERIAL PRIMARY KEY,
                indices INTEGER[]
            );
        """
    vector_size = get_vector_dim(table_name)
    if extension in [Extension.PGVECTOR_IVFFLAT, Extension.PGVECTOR_HNSW]:
        return f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id SERIAL PRIMARY KEY,
                v VECTOR({vector_size}),
                r REAL[{vector_size}]
            );
        """
    else:
        return f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id SERIAL PRIMARY KEY,
                v REAL[{vector_size}]
            );
        """


def create_table(extension, table_name):
    """Creates a table based on the extension and table name."""
    sql = get_create_table_query(extension, table_name)
    with DatabaseConnection(extension) as conn:
        conn.execute(sql)


def insert_table(extension, dest_table, source_csv):
    """Inserts data from a CSV file into the specified table."""
    if 'truth' in dest_table:
        sql = f"COPY {dest_table} (indices) FROM '{source_csv}' WITH csv"
    elif extension == Extension.PGVECTOR_IVFFLAT or extension == Extension.PGVECTOR_HNSW:
        sql = f"COPY {dest_table} (r) FROM '{source_csv}' WITH csv"
    else:
        sql = f"COPY {dest_table} (v) FROM '{source_csv}' WITH csv"
    with DatabaseConnection(extension) as conn:
        with open(source_csv, 'r') as f:
            conn.copy_expert(sql, f)
        if not 'truth' in dest_table and extension in [Extension.PGVECTOR_IVFFLAT, Extension.PGVECTOR_HNSW]:
            sql = f"UPDATE {dest_table} SET v = r; ALTER TABLE {dest_table} DROP COLUMN r;"
            conn.execute(sql)


# List of tables and their corresponding vector sizes
TABLES = [
    "sift_base10k",
    "sift_base100k",
    "sift_base200k",
    "sift_base400k",
    "sift_base600k",
    "sift_base800k",
    "sift_base1m",
    # "sift_base1b",

    "sift_query10k",
    "sift_query1m",
    "sift_query1b",

    "sift_truth10k",
    "sift_truth100k",
    "sift_truth200k",
    "sift_truth400k",
    "sift_truth600k",
    "sift_truth800k",
    "sift_truth1m",
    "sift_truth2m",
    "sift_truth5m",
    "sift_truth10m",
    "sift_truth20m",
    "sift_truth50m",
    "sift_truth100m",
    "sift_truth200m",
    "sift_truth500m",

    "gist_base100k",
    "gist_base200k",
    "gist_base400k",
    "gist_base600k",
    "gist_base800k",
    "gist_base1m",

    "gist_query1m",

    "gist_truth100k",
    "gist_truth200k",
    "gist_truth400k",
    "gist_truth600k",
    "gist_truth800k",
    "gist_truth1m",
]


def create_or_download_table(datapath, extension, table_name):
    """
    Creates a table if it does not exist, and downloads and inserts data if the table 
    is empty. 
    """

    create_table(extension, table_name)

    if not has_rows(extension, table_name):

        # Download data if it doesn't exist
        source_file = os.path.join(datapath, f"{table_name}.csv")
        if not os.path.exists(source_file):
            print(f"Source file {source_file} does not exist. Downloading...")
            if not os.path.exists(datapath):
                os.makedirs(datapath)
            urllib.request.urlretrieve(
                f"https://storage.googleapis.com/lanterndata/datasets/{table_name}.csv", source_file)
            print("Download complete.")

        # Insert data into the table
        insert_table(extension, table_name, source_file)

        print(
            f"Inserted data into table {table_name} for extension {extension.value}")

    else:
        print(
            f"Table {table_name} already exists for extension {extension.value}. Skipping.")


if __name__ == "__main__":

    # Set up an argument parser for command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--datapath", default="/app/data",
                        help="Path to data directory")
    args = parser.parse_args()

    # Creates the databases if they don't exist
    for extension in Extension:
        extension_name = extension.value.split('_')[0]
        with DatabaseConnection(autocommit=True) as conn:
            exists = conn.select_one(
                "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (extension_name,))
            if exists is None:
                conn.execute(f"CREATE DATABASE {extension_name};")
                print(f"Created database {extension_name}.")
            else:
                print(f"Database {extension_name} already exists. Skipping.")

    # Enables the extensions if they are not already enabled
    for extension, name in EXTENSION_NAMES.items():
        with DatabaseConnection(extension) as conn:
            conn.execute(f"CREATE EXTENSION IF NOT EXISTS {name};")
        print(f"Extension {name} is enabled.")

    # Loop through each extension and table to ensure they are created and populated
    for extension in Extension:
        for table_name in TABLES:
            create_or_download_table(args.datapath, extension, table_name)

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
