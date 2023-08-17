import json
import plotly.graph_objects as go
from utils.delete_index import delete_index
from utils.create_index import create_index
from utils.constants import Metric
from utils.database import DatabaseConnection, run_pgbench
from utils.process import save_result, get_experiment_results_for_params
from utils.cli import parse_args
from utils.names import get_table_name
from utils.numbers import convert_string_to_number
from utils.print import get_title, print_labels, print_row
from utils.plot import plot_line, plot_line_with_stddev


def get_latency_metric(bulk):
    return Metric.SELECT_BULK_LATENCY if bulk else Metric.SELECT_LATENCY


def get_latency_stddev_metric(bulk):
    return Metric.SELECT_BULK_LATENCY_STDDEV if bulk else Metric.SELECT_LATENCY_STDDEV


def get_tps_metric(bulk):
    return Metric.SELECT_BULK_TPS if bulk else Metric.SELECT_TPS


def generate_performance_result(extension, dataset, N, K, bulk):
    base_table_name = get_table_name(dataset, N, type='base')
    query_table_name = get_table_name(dataset, N, type='query')
    N_number = convert_string_to_number(N)
    if bulk:
        query = f"""
            SELECT
                q.id AS query_id,
                ARRAY_AGG(b.id) AS base_ids
            FROM (
                SELECT
                    *
                FROM
                    {query_table_name}
                ORDER BY
                    RANDOM()
                LIMIT
                    100
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
                    {K}
            ) b ON true
            GROUP BY
                q.id
        """
    else:
        query = f"""
            \set id random(1, {N_number})

            SELECT *
            FROM {base_table_name}
            ORDER BY v <-> (
                SELECT v
                FROM {query_table_name}
                WHERE id = :id
            )
            LIMIT {K};
        """
    stdout, stderr, tps, latency_average, latency_stddev = run_pgbench(
        extension, query)

    shared_response = {
        'out': stdout,
        'err': stderr,
    }

    tps_response = {
        **shared_response,
        'metric_value': tps,
        'metric_type': get_tps_metric(bulk),
    }

    latency_average_response = {
        **shared_response,
        'metric_value': latency_average,
        'metric_type': get_latency_metric(bulk),
    }

    latency_stddev_response = {
        **shared_response,
        'metric_value': latency_stddev,
        'metric_type': get_latency_stddev_metric(bulk),
    }

    return tps_response, latency_average_response, latency_stddev_response


def generate_recall_result(extension, dataset, N, K):
    base_table_name = get_table_name(dataset, N, type='base')
    truth_table_name = get_table_name(dataset, N, type='truth')
    query_table_name = get_table_name(dataset, N, type='query')

    with DatabaseConnection(extension) as conn:
        query_ids_sql = f"SELECT id FROM {query_table_name} LIMIT 100"
        query_ids = conn.select(query_ids_sql)

        recall_at_k_sum = 0
        for query_id, in query_ids:
            truth_ids = conn.select_one(f"""
                SELECT
                    indices[1:{K}]
                FROM
                    {truth_table_name}
                WHERE
                    id = {query_id}
            """)[0]
            base_ids = conn.select(f"""
                SELECT
                    id - 1
                FROM
                    {base_table_name}
                ORDER BY
                    v <-> (
                        SELECT
                            v
                        FROM
                            {query_table_name}
                        WHERE
                            id = {query_id} 
                    )
                LIMIT {K}
            """)
            base_ids = list(map(lambda x: x[0], base_ids))
            recall_at_k_sum += len(set(truth_ids).intersection(base_ids))

    # Calculate the average recall for this K
    recall_at_k = recall_at_k_sum / len(query_ids) / K
    recall_response = {
        'metric_type': Metric.RECALL,
        'metric_value': recall_at_k,
    }
    return recall_response


def generate_result(extension, dataset, N, K_values, index_params={}, bulk=False):
    delete_index(extension, dataset, N)
    create_index(extension, dataset, N, index_params=index_params)

    print(get_title(extension, index_params, dataset, N))
    print_labels('K', 'Recall', 'TPS', 'Avg Latency (ms)',
                 'Stddev Latency (ms)')

    for K in K_values:
        save_result_params = {
            'extension': extension,
            'index_params': index_params,
            'dataset': dataset,
            'n': convert_string_to_number(N),
            'k': K,
        }

        tps_response, latency_average_response, latency_stddev_response = generate_performance_result(
            extension, dataset, N, K, bulk)
        recall_response = generate_recall_result(extension, dataset, N, K)
        save_result(**tps_response, **save_result_params)
        save_result(**latency_average_response, **save_result_params)
        save_result(**latency_stddev_response, **save_result_params)
        save_result(**recall_response, **save_result_params)

        print_row(
            str(K),
            "{:.2f}".format(recall_response['metric_value']),
            "{:.2f}".format(tps_response['metric_value']),
            "{:.2f}".format(latency_average_response['metric_value']),
            "{:.2f}".format(latency_stddev_response['metric_value']),
        )
    print()

    delete_index(extension, dataset, N)


# Given a mapping of extension to index_params and fixed parameter, support plotting latency vs. variable parameter
def generate_plot(configuration, dataset, fixed_param, fixed_param_value, variable_param, metric_type, metric_stddev_type=None):
    fig = go.Figure()
    for extension, index_params in configuration.items():
        metric_types = [
            metric_type, metric_stddev_type] if metric_stddev_type is not None else [metric_type]
        results = get_experiment_results_for_params(
            metric_types, extension, json.dumps(index_params), dataset, **{(fixed_param.value.upper()): fixed_param_value})
        if metric_stddev_type is not None:
            param_values, metric_values, metric_stddev_values = zip(*results)
            plot_line_with_stddev(fig, extension, index_params,
                                  param_values, metric_values, metric_stddev_values)
        else:
            param_values, metric_values = zip(*results)
            plot_line(fig, extension, index_params,
                      param_values, metric_values)
    fig.update_layout(
        title=f"{metric_type.value} vs. {variable_param.value} ({dataset.value}, {fixed_param.value.upper()}={fixed_param_value})",
        xaxis_title=variable_param.value,
        yaxis_title=metric_type.value,
    )
    fig.show()


if __name__ == '__main__':
    extension, index_params, dataset, N_values, K_values = parse_args(
        "select experiment", ['extension', 'N', 'K'])
    for N in N_values:
        generate_result(extension, dataset, N, K_values, index_params)
