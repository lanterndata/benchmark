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


def table_exists(conn, table):
    """Check if a table exists in the database."""
    try:
        with conn.cursor() as cur:
            cur.execute("""
            SELECT EXISTS (
                SELECT 1 
                FROM information_schema.tables 
                WHERE table_name = %s
            );
            """, (table,))
            exists = cur.fetchone()[0]
            return exists
    except Exception as e:
        print(f"Error checking if table {table} exists: {e}")
        return False


def has_rows(conn, table):
    """Check if the table has non-zero rows."""
    if not table_exists(conn, table):
        print(f"Table {table} does not exist.")
        return False
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {table};")
            count = cur.fetchone()[0]
            return count > 0
    except Exception as e:
        print(f"Error checking row count for table {table}: {e}")
        return False


def create_table(dest_table, vector_size):
    if 'query' in dest_table:
        sql = f"""
            CREATE TABLE IF NOT EXISTS {dest_table} (
                id SERIAL PRIMARY KEY,
                indices INTEGER[]
            );
        """
    else:
        sql = f"""
            CREATE TABLE IF NOT EXISTS {dest_table} (
                id SERIAL PRIMARY KEY,
                v VECTOR({vector_size})
            );
        """
    with conn.cursor() as cur:
        cur.execute(sql)
        conn.commit()


def insert_table(dest_table, source_csv):
    with conn.cursor() as cur:
        with open(source_csv, 'r') as f:
            if 'query' in dest_table:
                sql = f"COPY {dest_table} (indices) FROM '{source_csv}' WITH csv"
            else:
                sql = f"COPY {dest_table} (v) FROM '{source_csv}' WITH csv"
            cur.copy_expert(sql, f)
    conn.commit()


# Create tables if they don't exist
BASE_TABLES = [
    [128, "siftsmall", "siftsmall_base.csv", "sift_base10k"],
    [128, "siftsmall", "siftsmall_query.csv", "sift_query10k"],
    [128, "siftsmall", "siftsmall_truth.csv", "sift_truth10k"],

    [128, "sift", "sift_base.csv", "sift_base1m"],
    [128, "sift", "sift_query.csv", "sift_query1m"],
    [128, "sift", "sift_truth.csv", "sift_truth1m"],

    # [128, "siftbig", "bigann_base.csv", "sift_base1b"],
    # [128, "siftbig", "bigann_query.csv", "sift_query1b"],
    # [128, "siftbig/gnd", "idx_2M.csv", "sift_truth2m"],
    # [128, "siftbig/gnd", "idx_5M.csv", "sift_truth5m"],
    # [128, "siftbig/gnd", "idx_10M.csv", "sift_truth10m"],
    # [128, "siftbig/gnd", "idx_20M.csv", "sift_truth20m"],
    # [128, "siftbig/gnd", "idx_50M.csv", "sift_truth50m"],
    # [128, "siftbig/gnd", "idx_100M.csv", "sift_truth100m"],
    # [128, "siftbig/gnd", "idx_200M.csv", "sift_truth200m"],
    # [128, "siftbig/gnd", "idx_500M.csv", "sift_truth500m"],

    [960, "gist", "gist_base.csv", "gist_base1m"],
    [960, "gist", "gist_query.csv", "gist_query1m"],
    [960, "gist", "gist_truth.csv", "gist_truth1m"],
]
for vector_size, source_dir, source_file, dest_table in BASE_TABLES:
    create_table(dest_table, vector_size)
    if not has_rows(conn, dest_table):
        source_path = os.path.join(args.datapath, source_dir, source_file)
        if not os.path.exists(source_path):
            print(f"Source file {source_path} does not exist. Downloading...")
            if not os.path.exists(os.path.join(args.datapath, source_dir)):
                os.makedirs(os.path.join(args.datapath, source_dir))
            urllib.request.urlretrieve(
                f"https://storage.googleapis.com/lanterndata/{os.path.join(source_dir, source_file)}", source_path)
            print("Download complete.")
        insert_table(dest_table, source_path)
        print(f"Inserted data into {dest_table}")
    else:
        print(f"Table {dest_table} already exists. Skipping.")


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
