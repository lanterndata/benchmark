import os
import sys
import argparse
import logging
from .utils.create_index import create_custom_index
from .utils.constants import Extension, Metric, Dataset
from .utils import cli
from .utils.names import get_table_name
from .utils.process import save_result, get_experiment_results
from .utils.database import DatabaseConnection, run_pgbench
from .utils.print import print_labels, print_row, get_title
from .utils.numbers import convert_string_to_number
from .setup import create_table
from . import benchmark_select


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


def get_latency_stddev_metric(bulk):
    return Metric.INSERT_BULK_LATENCY_STDDEV if bulk else Metric.INSERT_LATENCY_STDDEV


def get_tps_metric(bulk):
    return Metric.INSERT_BULK_TPS if bulk else Metric.INSERT_TPS


def print_insert_title_and_labels(extension, index_params, dataset):
    print(get_title(extension, index_params, dataset))
    print_labels('N', 'TPS', 'Avg Latency (ms)', 'Stddev Latency (ms)')


def print_insert_row(N, tps, latency_average, latency_stddev):
    print_row(
        f"{N} - {N + 1000 - 1}",
        "{:.2f}".format(tps),
        "{:.2f}".format(latency_average),
        "{:.2f}".format(latency_stddev),
    )


def create_sequence(extension, bulk, start_N):
    sequence_name = "benchmark_insert_sequence"
    drop_sql = f"DROP SEQUENCE IF EXISTS {sequence_name};"
    if bulk:
        create_sql = f"CREATE SEQUENCE {sequence_name} START {start_N} INCREMENT BY 100;"
    else:
        create_sql = f"CREATE SEQUENCE {sequence_name} START {start_N};"
    with DatabaseConnection(extension) as conn:
        conn.execute(drop_sql)
        conn.execute(create_sql)
    return sequence_name


def generate_result(extension, dataset, N_string, index_params={}, bulk=False, K=None, max_N=sys.maxsize):
    # Create benchmark table
    source_table = get_table_name(dataset, N_string)
    delete_dest_table(extension, dataset)
    dest_table = create_dest_table(extension, dataset)

    # Initialize benchmarking sequence
    N = min(convert_string_to_number(N_string), max_N)
    start_N = int(N / 10)
    sequence_name = create_sequence(extension, bulk, start_N)

    # Initialize benchmarking table and index
    query = f"""
        INSERT INTO
            {dest_table} (v)
        SELECT v
        FROM
            {source_table}
        WHERE
            id < {start_N};
    """
    with DatabaseConnection(extension) as conn:
        conn.execute(query)
    create_dest_index(extension, dataset, index_params)

    print_insert_title_and_labels(extension, index_params, dataset)
    for iter_N in range(start_N, N, 1000):
        if bulk:
            id_query = f"id >= next_id AND id < next_id + 100"
            transactions = 10
        else:
            id_query = f"id = next_id"
            transactions = 1000
        query = f"""
            WITH next_id_table AS (
                SELECT nextval('{sequence_name}') AS next_id
            )
            INSERT INTO
                {dest_table} (v)
            SELECT v
            FROM
                {source_table}, next_id_table
            WHERE
                {id_query}
        """

        cpu_count = os.cpu_count() or 1
        stdout, stderr, tps, latency_average, latency_stddev = run_pgbench(
            extension, query, clients=cpu_count, threads=cpu_count, transactions=transactions)

        def save_insert_result(metric_type, metric_value):
            save_result(
                metric_type,
                metric_value,
                extension=extension,
                index_params=index_params,
                dataset=dataset,
                n=iter_N + 1000,
                out=stdout,
                err=stderr,
            )

        save_insert_result(get_latency_metric(bulk), latency_average)
        save_insert_result(get_latency_stddev_metric(bulk), latency_stddev)
        save_insert_result(get_tps_metric(bulk), tps)

        print_insert_row(iter_N, tps, latency_average, latency_stddev)

    print()

    if K is not None:
        recall_after_insert = benchmark_select.generate_recall(
            extension, dataset, N_string, K, base_table_name_input=dest_table)
        save_result(Metric.RECALL_AFTER_INSERT, recall_after_insert,
                    extension=extension, index_params=index_params, dataset=dataset, n=N, k=K)

    delete_dest_table(extension, dataset)


def print_results(dataset, bulk=False):
    metric_types = [get_tps_metric(bulk), get_latency_metric(
        bulk), get_latency_stddev_metric(bulk)]

    for extension in Extension:
        results = get_experiment_results(metric_types, extension, dataset)
        for index_params, param_results in results:
            print_insert_title_and_labels(extension, index_params, dataset)
            for N, tps, latency_average, latency_stddev in param_results:
                print_insert_row(N, tps, latency_average, latency_stddev)
            print('\n\n')


if __name__ == '__main__':
    # Set up parser
    parser = argparse.ArgumentParser(description="benchmark insert")
    cli.add_extension(parser, allow_no_index=True)
    cli.add_index_params(parser)
    cli.add_dataset(parser)
    cli.add_N(parser)
    cli.add_logging(parser)

    # Parse arguments
    parsed_args = parser.parse_args()
    dataset = Dataset(parsed_args.dataset)
    extension = Extension(parsed_args.extension)
    index_params = cli.parse_index_params(extension, parsed_args)
    N = parsed_args.N or '10k'
    logging.basicConfig(level=getattr(logging, parsed_args.log.upper()))

    # Generate result
    generate_result(extension, dataset, N, index_params)
