import os
import argparse
import urllib.request
from typing import Dict, List
from .utils.database import DatabaseConnection
from .utils.constants import Extension, EXTENSION_NAMES, EXTENSIONS_USING_VECTOR, get_vector_dim, SUGGESTED_DATASET_SIZES, Dataset, VALID_DATASETS
from .utils.names import get_table_name


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
    if extension in EXTENSIONS_USING_VECTOR:
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
    elif extension in EXTENSIONS_USING_VECTOR:
        sql = f"COPY {dest_table} (r) FROM '{source_csv}' WITH csv"
    else:
        sql = f"COPY {dest_table} (v) FROM '{source_csv}' WITH csv"
    with DatabaseConnection(extension) as conn:
        with open(source_csv, 'r') as f:
            conn.copy_expert(sql, f)
        if not 'truth' in dest_table and extension in EXTENSIONS_USING_VECTOR:
            sql = f"UPDATE {dest_table} SET v = r; ALTER TABLE {dest_table} DROP COLUMN r;"
            conn.execute(sql)


def create_or_download_table(datapath, extension, table_name):
    """
    Creates a table if it does not exist, and downloads and inserts data if the table 
    is empty. 
    """

    create_table(extension, table_name)

    if has_rows(extension, table_name):
        print(
            f"Table {table_name} exists for extension {extension.value} and has data. Skipping.")

    else:
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


def create_or_download_tables(datapath: str, extension: Extension, dataset_sizes: Dict[Dataset, List[str]]):
    table_names = set()
    for dataset, N_values in dataset_sizes.items():
        for N in N_values:
            table_names.add(get_table_name(dataset, N, type='base'))
            table_names.add(get_table_name(dataset, N, type='truth'))
            table_names.add(get_table_name(dataset, N, type='query'))
    for table_name in table_names:
        create_or_download_table(datapath, extension, table_name)


def setup_extension(datapath: str, extension: Extension, dataset_sizes: Dict[Dataset, List[str]] = SUGGESTED_DATASET_SIZES):
    # Create the database if it doesn't exist
    extension_name = extension.value.split('_')[0]
    with DatabaseConnection(autocommit=True) as conn:
        exists = conn.select_one(
            "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (extension_name,))
        if exists is None:
            conn.execute(f"CREATE DATABASE {extension_name};")
            print(f"Created database {extension_name}.")
        else:
            print(f"Database {extension_name} already exists. Skipping.")

    # Enables the extension if it is not already enabled
    extension_name = EXTENSION_NAMES[extension]
    with DatabaseConnection(extension) as conn:
        conn.execute(f"CREATE EXTENSION IF NOT EXISTS {extension_name};")
    print(f"Extension {extension_name} is enabled.")

    # Ensure all tables are created and populated
    create_or_download_tables(datapath, extension, dataset_sizes)


# Create the experiment_results table if it doesn't exist
# Useful for notebook experiments
def setup_results_table():
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Setup the database for benchmarking')
    parser.add_argument("--datapath",
                        default="/app/data", help="Path to save data used for benchmarking")
    parser.add_argument("--extension",
                        nargs='+', help="Extensions to setup benchmarking for")
    parser.add_argument("--dataset",
                        choices=[d for d in VALID_DATASETS], help="Dataset name")
    parser.add_argument("--N",
                        nargs='+', help="Dataset sizes")
    args = parser.parse_args()

    setup_results_table()

    dataset_sizes = SUGGESTED_DATASET_SIZES
    if args.dataset is not None and args.N is not None:
        dataset_sizes = {Dataset(args.dataset): args.N}

    if args.extension is None:
        for extension in Extension:
            setup_extension(args.datapath, extension, dataset_sizes)
    else:
        for extension in args.extension:
            setup_extension(args.datapath, Extension(extension), dataset_sizes)
    print('Done!')
