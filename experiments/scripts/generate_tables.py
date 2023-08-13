import os
import time
import psycopg2

BASE_TABLES = [
    [128, "siftsmall", "siftsmall_base.csv", "sift_base10k"],
    [128, "siftsmall", "siftsmall_query.csv", "sift_query10k"],
    [128, "siftsmall", "siftsmall_truth.csv", "sift_truth10k"],

    [128, "sift", "sift_base.csv", "sift_base1m"],
    [128, "sift", "sift_query.csv", "sift_query1m"],
    [128, "sift", "sift_truth.csv", "sift_truth1m"],

    [128, "siftbig", "bigann_base.csv", "sift_base1b"],
    [128, "siftbig", "bigann_query.csv", "sift_query1b"],
    [128, "siftbig/gnd", "idx_2M.csv", "sift_truth2m"],
    [128, "siftbig/gnd", "idx_5M.csv", "sift_truth5m"],
    [128, "siftbig/gnd", "idx_10M.csv", "sift_truth10m"],
    [128, "siftbig/gnd", "idx_20M.csv", "sift_truth20m"],
    [128, "siftbig/gnd", "idx_50M.csv", "sift_truth50m"],
    [128, "siftbig/gnd", "idx_100M.csv", "sift_truth100m"],
    [128, "siftbig/gnd", "idx_200M.csv", "sift_truth200m"],
    [128, "siftbig/gnd", "idx_500M.csv", "sift_truth500m"],

    [960, "gist", "gist_base.csv", "gist_base1m"],
    [960, "gist", "gist_query.csv", "gist_query1m"],
    [960, "gist", "gist_truth.csv", "gist_truth1m"],
]


def convert_existing_csvs():

    for _, folder, file, table in BASE_TABLES:
        source_file = os.path.join('/app/data', folder, file)
        dest_file = os.path.join('/app/data/new_data', table + '.csv')
        t1 = time.time()
        if 'truth' in table:
            # Copy source file to test file
            os.system(f"cp {source_file} {dest_file}")
        else:
            # Convert vector CSV to real CSV by replacing [ with { and ] with }
            os.system(
                'sed -e "s/\\[/{{/g" -e "s/\\]/}}/g" {} > {}'.format(source_file, dest_file))
        t2 = time.time()
        print(f"Copied {source_file} to {dest_file} in {(t2 - t1):.2f}s")


def dump_derived_tables():
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor()
    for dataset in ["sift", "gist"]:
        for N in ['100k', '200k', '400k', '600k', '800k']:
            table = f"{dataset}_base{N}"
            file = f"/app/data/new_data/{table}.csv"

            sql = f"COPY (SELECT v FROM {table} ORDER BY id) TO '{file}' WITH CSV"
            cur.execute(sql)
            conn.commit()

            os.system(
                'sed -i -e "s/\\[/{{/g" -e "s/\\]/}}/g" {}'.format(file))
            print(f"Copied {table} to {file}")

    cur.close()
    conn.close()


def create_and_dump_new_truth_tables():
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor()

    # Create new truth tables and dump to CSVs in new folder
    for dataset, num_query in [("sift", 10000), ("gist", 1000)]:
        query_table_name = f"{dataset}_query1m"
        for N in ['100k', '200k', '400k', '600k', '800k']:
            base_table_name = f"{dataset}_base{N}"
            truth_table_name = f"{dataset}_truth{N}"

            sql = f"""
                DROP TABLE IF EXISTS {truth_table_name};

                DROP INDEX IF EXISTS {base_table_name}_index;

                CREATE TABLE {truth_table_name} (
                    id SERIAL PRIMARY KEY,
                    indices INTEGER[]
                );
            """
            cur.execute(sql)

            for N in range(100, num_query + 1, 100):
                print(
                    f"Creating rows {N - 100} - {N - 1} of {truth_table_name}")
                sql = f"""
                    INSERT INTO {truth_table_name}
                    SELECT
                        q.id,
                        ARRAY_AGG(b.id ORDER BY q.v <-> b.v)
                    FROM (
                        SELECT *
                        FROM
                            {query_table_name}
                        WHERE
                            id >= {N - 100} AND id < {N}
                    ) q
                    JOIN LATERAL (
                        SELECT
                            id,
                            v
                        FROM
                            {base_table_name}
                        ORDER BY
                            q.v <-> v
                        LIMIT
                            100
                    ) b ON true
                    GROUP BY
                        q.id;
                """
                cur.execute(sql)
                conn.commit()
                print(
                    f"Created rows {N - 100} - {N - 1} of {truth_table_name}")

            sql = f"COPY (SELECT indices FROM {truth_table_name} ORDER BY id) TO '/app/data/new_data/{truth_table_name}.csv' WITH CSV;"
            print(f"Dumped {truth_table_name}")

    cur.close()
    conn.close()


create_and_dump_new_truth_tables()
