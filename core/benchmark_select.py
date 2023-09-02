import re
import argparse
import statistics
from .utils.delete_index import delete_index
from .utils.create_index import create_index
from .utils.constants import Metric, Dataset, Extension, SUGGESTED_K_VALUES
from .utils.database import DatabaseConnection, run_pgbench
from .utils.process import save_result
from .utils import cli
from .utils.names import get_table_name
from .utils.numbers import convert_string_to_number
from .utils.print import get_title, print_labels, print_row


def get_performance_query(dataset, N, K, bulk, id=None):
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
        set_id_sql = f"\set id random(1, {N_number})" if id is None else ""
        query_id_sql = ":id" if id is None else id
        query = f"""
            {set_id_sql}

            SELECT *
            FROM
                {base_table_name}
            ORDER BY v <-> (
                SELECT v
                FROM
                    {query_table_name}
                WHERE
                    id = {query_id_sql}
            )
            LIMIT {K};
        """
    return query


def generate_performance_result(extension, dataset, N, K, bulk):
    query = get_performance_query(dataset, N, K, bulk)
    stdout, stderr, tps, latency_average, latency_stddev = run_pgbench(
        extension, query)

    shared_response = {
        'out': stdout,
        'err': stderr,
    }

    tps_response = {
        **shared_response,
        'metric_value': tps,
        'metric_type': Metric.SELECT_BULK_TPS if bulk else Metric.SELECT_TPS,
    }

    latency_average_response = {
        **shared_response,
        'metric_value': latency_average,
        'metric_type': Metric.SELECT_BULK_LATENCY if bulk else Metric.SELECT_LATENCY,
    }

    latency_stddev_response = {
        **shared_response,
        'metric_value': latency_stddev,
        'metric_type': Metric.SELECT_BULK_LATENCY_STDDEV if bulk else Metric.SELECT_LATENCY_STDDEV,
    }

    return tps_response, latency_average_response, latency_stddev_response


def generate_utilization_result_one(extension, dataset, N, K, bulk, id):
    query = f"""
        EXPLAIN (ANALYZE, BUFFERS TRUE)
        {get_performance_query(dataset, N, K, bulk, id)}
    """
    with DatabaseConnection(extension) as conn:
        response = conn.select(query)

    start_search = False
    for line, in response:
        if start_search and 'Buffers' in line:
            shared_hit_match = re.search(r'shared hit=(\d+)', line)
            read_match = re.search(r'read=(\d+)', line)

            shared_hit_value, read_value = 0, 0

            if shared_hit_match:
                shared_hit_value = int(shared_hit_match.group(1))
            if read_match:
                read_value = int(read_match.group(1))
            return shared_hit_value, read_value
        if ' <-> ' in line:
            start_search = True


def generate_utilization_result(extension, dataset, N, K, bulk):
    shared_hit_values, read_values = [], []
    for id in range(1, 10):
        shared_hit_value, read_value = generate_utilization_result_one(
            extension, dataset, N, K, bulk, id)
        shared_hit_values.append(shared_hit_value)
        read_values.append(read_value)

    shared_hit_response = {
        'metric_type': Metric.BUFFER_BULK_SHARED_HIT_COUNT if bulk else Metric.BUFFER_SHARED_HIT_COUNT,
        'metric_value': statistics.mean(shared_hit_values),
    }

    shared_hit_stddev_response = {
        'metric_type': Metric.BUFFER_BULK_SHARED_HIT_COUNT_STDDEV if bulk else Metric.BUFFER_SHARED_HIT_COUNT_STDDEV,
        'metric_value': statistics.stdev(shared_hit_values),
    }

    read_response = {
        'metric_type': Metric.BUFFER_BULK_READ_COUNT if bulk else Metric.BUFFER_READ_COUNT,
        'metric_value': statistics.mean(read_values),
    }

    read_stddev_response = {
        'metric_type': Metric.BUFFER_BULK_READ_COUNT_STDDEV if bulk else Metric.BUFFER_READ_COUNT_STDDEV,
        'metric_value': statistics.stdev(read_values),
    }

    return shared_hit_response, shared_hit_stddev_response, read_response, read_stddev_response


def generate_recall_result(extension, dataset, N, K):
    base_table_name = get_table_name(dataset, N, type='base')
    truth_table_name = get_table_name(dataset, N, type='truth')
    query_table_name = get_table_name(dataset, N, type='query')

    with DatabaseConnection(extension) as conn:
        query_ids_sql = f"SELECT id FROM {query_table_name} LIMIT 100"
        query_ids = conn.select(query_ids_sql)

        recall_at_k_sum = 0
        sql = f"""
            WITH q AS (
                SELECT
                    id,
                    v
                FROM
                    {query_table_name}
                LIMIT
                    100
            )
            SELECT
                array_agg(b.id) as base_ids,
                t.indices[1:{K}] as truth_ids
            FROM q
            JOIN LATERAL (
                SELECT
                    id
                FROM
                    {base_table_name}
                ORDER BY
                    {base_table_name}.v <-> q.v
                LIMIT
                    {K}
            ) b ON TRUE
            LEFT JOIN
                {truth_table_name} AS t
            ON
                t.id = q.id
            GROUP BY
                q.id,
                t.indices
        """
        results = conn.select(sql)
        for base_ids, truth_ids in results:
            truth_id_set = set(truth_ids)
            # TODO: Fix dataset off by 1 error
            recall_at_k_result = max(
                len(truth_id_set.intersection(base_ids)),
                len(truth_id_set.intersection(map(lambda id: id - 1, base_ids))))
            recall_at_k_sum += recall_at_k_result
            print(truth_ids, base_ids, recall_at_k_result)

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
                 'Stddev Latency (ms)', 'Buffer Shared Hit', 'Buffer Read')

    for K in K_values:
        def save_select_result(response):
            save_result(
                **response,
                extension=extension,
                index_params=index_params,
                dataset=dataset,
                n=convert_string_to_number(N),
                k=K,
            )

        tps_response, latency_average_response, latency_stddev_response = generate_performance_result(
            extension, dataset, N, K, bulk)
        recall_response = generate_recall_result(extension, dataset, N, K)
        shared_hit_response, shared_hit_stddev_response, read_response, read_stddev_response = generate_utilization_result(
            extension, dataset, N, K, bulk)
        save_select_result(tps_response)
        save_select_result(latency_average_response)
        save_select_result(latency_stddev_response)
        save_select_result(recall_response)
        save_select_result(shared_hit_response)
        save_select_result(shared_hit_stddev_response)
        save_select_result(read_response)
        save_select_result(read_stddev_response)

        print_row(
            str(K),
            "{:.2f}".format(recall_response['metric_value']),
            "{:.2f}".format(tps_response['metric_value']),
            "{:.2f}".format(latency_average_response['metric_value']),
            "{:.2f}".format(latency_stddev_response['metric_value']),
            "{:.2f}".format(shared_hit_response['metric_value']),
            "{:.2f}".format(read_response['metric_value']),
        )
    print()

    delete_index(extension, dataset, N)


if __name__ == '__main__':
   # Set up parser
    parser = argparse.ArgumentParser(description="benchmark select")
    cli.add_extension(parser)
    cli.add_index_params(parser)
    cli.add_dataset(parser)
    cli.add_N(parser)
    cli.add_K_values(parser)

    # Parse arguments
    parsed_args = parser.parse_args()
    dataset = Dataset(parsed_args.dataset)
    extension = Extension(parsed_args.extension)
    index_params = cli.parse_index_params(extension, parsed_args)
    N = parsed_args.N or '10k'
    K_values = parsed_args.K or SUGGESTED_K_VALUES

    # Generate result
    generate_result(extension, dataset, N, K_values, index_params)
