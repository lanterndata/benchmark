import os
import psycopg2
import plotly.graph_objects as go
from scripts.create_index import create_custom_index
from scripts.script_utils import get_table_name, save_result, execute_sql, VALID_EXTENSIONS_AND_NONE, get_experiment_results, parse_args
from scripts.number_utils import convert_number_to_string
from utils.colors import get_color_from_extension
from utils.print import print_labels, print_row
import time

N_INTERVAL = 1000
N_MIN = 5000
N_MAX = 40000


def get_dest_table_name(dataset):
    return dataset + '_insert'


def get_dest_index_name(dataset):
    return get_dest_table_name(dataset) + '_index'


def create_dest_table(dataset):
    table_name = get_dest_table_name(dataset)
    vector_dim = 128 if dataset == 'sift' else 960
    sql = f"""
      CREATE TABLE IF NOT EXISTS {table_name} (
        id SERIAL PRIMARY KEY,
        v VECTOR({vector_dim})
      )
    """
    execute_sql(sql)
    return table_name


def create_dest_index(extension, dataset, index_params):
    table = get_dest_table_name(dataset)
    index = get_dest_index_name(dataset)
    create_custom_index(extension, table, index, index_params)


def delete_dest_table(dataset):
    table_name = get_dest_table_name(dataset)
    sql = f"DROP TABLE IF EXISTS {table_name}"
    execute_sql(sql)


def get_metric_type(bulk):
    return 'insert bulk (latency s)' if bulk else 'insert (latency s)'


def generate_result(extension, dataset, index_params={}, bulk=False):
    db_connection_string = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(db_connection_string)
    cur = conn.cursor()

    source_table = get_table_name(dataset, '1m')
    delete_dest_table(dataset)
    dest_table = create_dest_table(dataset)

    if N_MIN > 0:
        query = f"""
            INSERT INTO
                {dest_table}
            SELECT *
            FROM
                {source_table}
            WHERE
                id < {N_MIN}
        """
        execute_sql(query)

    create_dest_index(extension, dataset, index_params)

    result_params = {
        'metric_type': get_metric_type(bulk),
        'database': extension,
        'database_params': index_params,
        'dataset': dataset,
        'conn': conn,
        'cur': cur,
    }

    print(
        f"extension: {extension}, dataset: {dataset}, index_params: {index_params}")
    if bulk:
        for N in range(N_MIN + N_INTERVAL, N_MAX + 1, N_INTERVAL):
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
                metric_value=insert_latency,
                n=N,
                **result_params
            )
            print(f"{N - N_INTERVAL} - {N - 1}:".ljust(16),
                  "{:.2f}".format(insert_latency) + 's')
    else:
        t1 = time.time()
        for N in range(N_MIN, N_MAX):
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
            if (N + 1) % N_INTERVAL == 0:
                t2 = time.time()
                insert_latency = t2 - t1
                save_result(
                    metric_value=insert_latency,
                    n=N + 1,
                    **result_params
                )
                print(f"{N + 1 - N_INTERVAL} - {N}:".ljust(16),
                      "{:.2f}".format(insert_latency) + 's')
                t1 = time.time()
    print()

    delete_dest_table(dataset)

    cur.close()
    conn.close()


def print_results(dataset, bulk=False):
    metric_type = get_metric_type(bulk)
    for extension in VALID_EXTENSIONS_AND_NONE:
        results = get_experiment_results(metric_type, extension, dataset)
        if len(results) == 0:
            print(f"No results for {extension}")
            print("\n\n")
        for (database_params, param_results) in results:
            print(database_params)
            print_labels(dataset + ' - ' + extension, 'N', 'latency (s)')
            for N, latency in param_results:
                print_row(convert_number_to_string(
                    N), "{:.2f}".format(latency))
            print('\n\n')


def plot_results(dataset, bulk=False):
    metric_type = get_metric_type(bulk)

    fig = go.Figure()
    for extension in VALID_EXTENSIONS_AND_NONE:
        results = get_experiment_results(metric_type, extension, dataset)
        for index, (database_params, param_results) in enumerate(results):
            x_values, y_values = zip(*param_results)
            color = get_color_from_extension(extension, index=index)
            fig.add_trace(go.Scatter(
                x=x_values,
                y=y_values,
                marker=dict(color=color),
                mode='lines+markers',
                name=f"{extension} - {database_params}",
            ))
    fig.update_layout(
        title=f"{dataset} - {metric_type}",
        xaxis_title=f"latency of inserting last {N_INTERVAL} rows",
        yaxis_title='latency (s)',
    )
    fig.show()


if __name__ == '__main__':
    extension, index_params, dataset, _, _ = parse_args(
        "insert experiment", ['extension'])
    generate_result(extension, dataset, index_params)
