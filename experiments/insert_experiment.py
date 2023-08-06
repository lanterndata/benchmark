import os
import argparse
import psycopg2
import plotly.graph_objects as go
from scripts.script_utils import get_table_name, save_result, VALID_DATASETS, execute_sql, VALID_EXTENSIONS_AND_NONE
from utils.colors import get_color_from_extension
import time

N_INTERVAL = 1000
N_MAX = 40000

def get_dest_table_name(dataset):
    return dataset + '_insert'

def get_dest_index_name(dataset):
    return get_dest_table_name(dataset) + '_index'

def create_dest_table(dataset):
    table_name = get_dest_table_name(dataset)
    sql = f"""
      CREATE TABLE IF NOT EXISTS {table_name} (
        id SERIAL PRIMARY KEY,
        v VECTOR(128)
      )
    """
    execute_sql(sql)
    return table_name

def create_dest_index(extension, dataset):
    sql = ''
    table = get_dest_table_name(dataset)
    index = get_dest_index_name(dataset)
    if extension == 'pgvector':
        sql = f"""
            CREATE INDEX IF NOT EXISTS {index} ON {table} USING
            ivfflat (v) WITH (lists = 100)
        """
    elif extension == 'lantern':
        sql = f"""
            CREATE INDEX IF NOT EXISTS {index} ON {table} USING
            hnsw (v)
        """
    if sql != '':
        execute_sql(sql)

def delete_dest_table(dataset):
    table_name = get_dest_table_name(dataset)
    sql = f"DROP TABLE IF EXISTS {table_name}"
    execute_sql(sql)

def generate_result(extension, dataset, bulk=False):
    db_connection_string = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(db_connection_string)
    cur = conn.cursor()

    source_table = get_table_name(dataset, '1m')
    delete_dest_table(dataset)
    dest_table = create_dest_table(dataset)
    create_dest_index(extension, dataset)

    result_params = {
        'conn': conn,
        'cur': cur,
    }

    if bulk:
        for N in range(N_INTERVAL, N_MAX, N_INTERVAL):
            query = f"""
                INSERT INTO
                    {dest_table}
                SELECT *
                FROM
                    {source_table}
                WHERE
                    id < {N}
                    AND id >= {N - N_INTERVAL}
            """
            t1 = time.time()
            execute_sql(query)
            t2 = time.time()
            insert_latency = t2 - t1
            save_result(
                metric_type='insert bulk (latency ms)',
                metric_value=insert_latency,
                n=N,
                **result_params
            )
    else:
        t1 = time.time()
        for N in range(N_MAX):
            query = f"""
                INSERT INTO
                    {dest_table}
                SELECT *
                FROM
                    {source_table}
                WHERE
                    id = {N}
            """ 
            execute_sql(query)
            if N % N_INTERVAL == 0 and N > 0:
                t2 = time.time()
                insert_latency = t2 - t1
                save_result(
                    metric_type='insert (latency ms)',
                    metric_value=insert_latency,
                    n=N,
                    **result_params
                )
                t1 = time.time()
    
    delete_dest_table(dataset)

    cur.close()
    conn.close()

def plot_results(dataset, bulk=False):
    metric_type = 'insert bulk (latency ms)' if bulk else 'insert (latency ms)'

    # Process data
    plot_items = []
    for extension in VALID_EXTENSIONS_AND_NONE:
        sql = f"""
            SELECT
                N,
                metric_value
            FROM
                experiment_results
            WHERE
                metric_type = %s
                AND database = %s
                AND dataset = %s
            ORDER BY
                N
        """
        data = (metric_type, extension, dataset)
        values = execute_sql(sql, data, select=True)
        if len(values) == 0:
            continue
        x_values, y_values = zip(*values)
        color = get_color_from_extension(extension)
        plot_items.append((extension, x_values, y_values, color))

    # Plot data
    fig = go.Figure()
    for (key, x_values, y_values, color) in plot_items:
        fig.add_trace(go.Scatter(
            x=x_values,
            y=y_values,
            marker=dict(color=color),
            mode='lines+markers',
            name=key
        ))
    fig.update_layout(
        title=metric_type,
        xaxis_title='latency of inserting last 1000 rows',
        yaxis_title='latency (ms)',
    )
    fig.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="insert experiment")
    parser.add_argument("--dataset", type=str, choices=VALID_DATASETS.keys(), required=True, help="output file name (required)")
    parser.add_argument('--extension', type=str, choices=VALID_EXTENSIONS_AND_NONE, required=True, help='extension type')
    args = parser.parse_args()
    
    extension = args.extension
    dataset = args.dataset

    generate_result(extension, dataset)