import os
import psycopg2
import plotly.graph_objects as go
from scripts.create_index import create_custom_index
from scripts.script_utils import (
    get_table_name, save_result, execute_sql, VALID_EXTENSIONS_AND_NONE, get_experiment_results,
    get_distinct_database_params, parse_args, run_pgbench, get_schema_name, get_vector_dim
)
from scripts.number_utils import convert_number_to_string
from utils.print import print_labels, print_row
from utils.colors import get_color_from_extension


def get_dest_table_name(extension, dataset):
    schema = get_schema_name(extension)
    return f"{schema}.{dataset}_insert"


def get_dest_index_name(extension, dataset):
    return get_dest_table_name(extension, dataset) + '_index'


def create_dest_table(extension, dataset):
    schema = get_schema_name(extension)
    table_name = get_dest_table_name(extension, dataset)
    vector_dim = get_vector_dim(dataset)
    sql = f"""
      CREATE TABLE IF NOT EXISTS {schema}.{table_name} (
        id SERIAL PRIMARY KEY,
        v VECTOR({vector_dim})
      )
    """
    execute_sql(sql)
    return table_name


def create_dest_index(extension, dataset, index_params):
    table = get_dest_table_name(extension, dataset)
    index = get_dest_index_name(extension, dataset)
    create_custom_index(extension, table, index, index_params)


def delete_dest_table(extension, dataset):
    table_name = get_dest_table_name(extension, dataset)
    sql = f"DROP TABLE IF EXISTS {table_name}"
    execute_sql(sql)


def get_latency_metric(bulk):
    return 'insert bulk (latency ms)' if bulk else 'insert (latency ms)'


def get_tps_metric(bulk):
    return 'insert bulk (tps)' if bulk else 'insert (tps)'


def get_metric_types(bulk):
    return [get_tps_metric(bulk), get_latency_metric(bulk)]


def generate_result(extension, dataset, index_params={}, bulk=False):
    db_connection_string = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(db_connection_string)
    cur = conn.cursor()

    source_table = get_table_name(extension, dataset, '1m')
    delete_dest_table(extension, dataset)
    dest_table = create_dest_table(extension, dataset)

    query = f"""
        INSERT INTO
            {dest_table} (v)
        SELECT v
        FROM
            {source_table}
        WHERE
            id < 10000
    """
    execute_sql(query)

    create_dest_index(extension, dataset, index_params)

    print(
        f"extension: {extension}, dataset: {dataset}, index_params: {index_params}")
    print("N".ljust(16), "TPS".ljust(10), "Latency (ms)")
    print('-' * 42)
    for N in range(10000, 20001, 1000):

        if bulk:
            id_query = "id >= :id AND id < :id + 100"
            transactions = 10
        else:
            id_query = "id = :id"
            transactions = 1000
        query = f"""
            \set id random(1, 1000000)

            INSERT INTO
                {dest_table} (v)
            SELECT v
            FROM
                {source_table}
            WHERE
                {id_query};
        """

        stdout, stderr, tps, latency = run_pgbench(
            query, clients=1, transactions=transactions)

        save_result_params = {
            'database': extension,
            'database_params': index_params,
            'dataset': dataset,
            'n': N,
            'out': stdout,
            'err': stderr,
            'conn': conn,
            'cur': cur,
        }
        save_result(get_latency_metric(bulk), latency, **save_result_params)
        save_result(get_tps_metric(bulk), tps, **save_result_params)
        print(
            f"{N} - {N + 1000 - 1}".ljust(16),
            "{:.2f}".format(tps).ljust(10),
            "{:.2f}".format(latency).ljust(15)
        )

    print()

    delete_dest_table(extension, dataset)

    cur.close()
    conn.close()


def print_results(dataset, bulk=False):
    metric_types = get_metric_types(bulk)

    for extension in VALID_EXTENSIONS_AND_NONE:
        database_params_list = get_distinct_database_params(
            metric_types, extension, dataset)

        for database_params in database_params_list:
            sql = """
                SELECT
                    N,
                    MAX(CASE WHEN metric_type = %s THEN metric_value ELSE NULL END),
                    MAX(CASE WHEN metric_type = %s THEN metric_value ELSE NULL END)
                FROM
                    experiment_results
                WHERE
                    metric_type = ANY(%s)
                    AND database = %s
                    AND database_params = %s
                    AND dataset = %s
                GROUP BY
                    N
                ORDER BY
                    N
            """
            data = (metric_types[0], metric_types[1],
                    metric_types, extension, database_params, dataset)
            results = execute_sql(sql, data=data, select=True)

            title = f"{extension} - {dataset} - {database_params}"
            print_labels(title, 'N', 'TPS', 'latency (s)')
            for N, tps, latency in results:
                print_row(
                    convert_number_to_string(N),
                    "{:.2f}".format(tps),
                    "{:.2f}".format(latency)
                )
            print('\n\n')


def plot_results(dataset, bulk=False):
    metric_types = get_metric_types(bulk)
    for metric_type in metric_types:
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
            xaxis_title=f"latency of inserting 8000 rows",
            yaxis_title='latency (s)',
        )
        fig.show()


if __name__ == '__main__':
    extension, index_params, dataset, _, _ = parse_args(
        "insert experiment", ['extension'])
    generate_result(extension, dataset, index_params)
