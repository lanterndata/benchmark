import plotly.graph_objects as go
from utils.create_index import create_custom_index
from utils.constants import Extension, Metric
from utils.cli import parse_args
from utils.names import get_table_name
from utils.process import save_result, get_experiment_results
from utils.database import DatabaseConnection, run_pgbench
from utils.numbers import convert_number_to_string
from utils.print import print_labels, print_row, get_title
from utils.colors import get_color_from_extension
from .setup_tables import create_table


def get_dest_table_name(dataset):
    return f"{dataset.value}_insert"


def get_dest_index_name(dataset):
    return get_dest_table_name(dataset) + '_index'


def create_dest_table(extension, dataset):
    table_name = get_dest_table_name(dataset)
    create_table(extension, table_name)
    return table_name


def create_dest_index(extension, dataset, index_params):
    table = get_dest_table_name(dataset)
    index = get_dest_index_name(dataset)
    create_custom_index(extension, table, index, index_params)


def delete_dest_table(extension, dataset):
    table_name = get_dest_table_name(dataset)
    sql = f"DROP TABLE IF EXISTS {table_name}"
    with DatabaseConnection(extension) as conn:
        conn.execute(sql)


def get_latency_metric(bulk):
    return Metric.INSERT_BULK_LATENCY if bulk else Metric.INSERT_LATENCY


def get_tps_metric(bulk):
    return Metric.INSERT_BULK_TPS if bulk else Metric.INSERT_TPS


def get_metric_types(bulk):
    return [get_tps_metric(bulk), get_latency_metric(bulk)]


def generate_result(extension, dataset, index_params={}, bulk=False):
    source_table = get_table_name(dataset, '1m')
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
    with DatabaseConnection(extension) as conn:
        conn.execute(query)

    create_dest_index(extension, dataset, index_params)

    print(get_title(extension, index_params, dataset))
    print_labels('N', 'TPS', 'latency (ms)')
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
            extension, query, clients=1, transactions=transactions)

        save_result_params = {
            'extension': extension,
            'index_params': index_params,
            'dataset': dataset,
            'n': N,
            'out': stdout,
            'err': stderr,
        }
        save_result(get_latency_metric(bulk), latency, **save_result_params)
        save_result(get_tps_metric(bulk), tps, **save_result_params)
        print_row(
            f"{N} - {N + 1000 - 1}".ljust(16),
            "{:.2f}".format(tps).ljust(10),
            "{:.2f}".format(latency).ljust(15)
        )

    print()

    delete_dest_table(extension, dataset)


def print_results(dataset, bulk=False):
    metric_types = get_metric_types(bulk)

    for extension in Extension:
        results = get_experiment_results(metric_types, extension, dataset)
        for index_params, param_results in results:
            print(get_title(extension, index_params, dataset))
            print_labels('N', 'TPS', 'latency (s)')
            for N, tps, latency in param_results:
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
        for extension in Extension:
            results = get_experiment_results(metric_type, extension, dataset)
            for index, (index_params, param_results) in enumerate(results):
                x_values, y_values = zip(*param_results)
                color = get_color_from_extension(extension, index=index)
                fig.add_trace(go.Scatter(
                    x=x_values,
                    y=y_values,
                    marker=dict(color=color),
                    mode='lines+markers',
                    name=f"{extension.value.upper()} - {index_params}",
                ))
        fig.update_layout(
            title=f"{dataset.value} - {metric_type.value}",
            xaxis_title=f"latency of inserting 8000 rows",
            yaxis_title='latency (s)',
        )
        fig.show()


if __name__ == '__main__':
    extension, index_params, dataset, _, _ = parse_args(
        "insert experiment", ['extension'])
    generate_result(extension, dataset, index_params)
