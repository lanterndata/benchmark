import time
import argparse
import logging
import subprocess
import statistics
import json
from .utils.database import DatabaseConnection, get_database_url
from .utils.delete_index import delete_index
from .utils.create_index import get_create_index_query, get_index_name
from .utils.create_external_index import create_external_index
from .utils.numbers import convert_string_to_number, convert_number_to_string, convert_number_to_bytes
from .utils.constants import Metric, Extension, Dataset
from .utils import cli
from .utils.process import save_result, get_experiment_results
from .utils.print import print_labels, print_row, get_title
from .utils.cloud_provider import get_cloud_provider
from .utils.names import get_cloud_index_name, get_table_name

SUPPRESS_COMMAND = "SET client_min_messages TO WARNING"

VALID_EXTENSIONS = [e for e in Extension if e != Extension.NONE]


def validate_extension(extension):
    assert extension != Extension.NONE


def generate_disk_usage_result(extension, dataset, N):
    index = get_index_name(dataset, N)
    sql = f"SELECT pg_total_relation_size('{index}')"
    with DatabaseConnection(extension) as conn:
        disk_usage = conn.select_one(sql)[0]
    return disk_usage


def generate_external_performance_result(extension, dataset, N, index_params):
    t1 = time.time()
    create_external_index(extension, dataset, N, index_params)
    t2 = time.time()
    return (t2 - t1) * 1000

def generate_cloud_performance_result(provider_instance, vector_data, index_params):
    t1 = time.time()
    provider_instance.create_index(index_params, vector_data)
    t2 = time.time()
    return (t2 - t1) * 1000

def generate_performance_result(extension, dataset, N, index_params):
    if 'external' in index_params and index_params['external']:
        return generate_external_performance_result(extension, dataset, N, index_params)
    create_index_query = get_create_index_query(
        extension, dataset, N, index_params)
    result = subprocess.run(["psql", get_database_url(extension), "-c", SUPPRESS_COMMAND, "-c",
                             "\\timing", "-c", create_index_query], capture_output=True, text=True)
    lines = result.stdout.splitlines()
    for line in lines:
        if line.startswith("Time:"):
            time = float(line.split(":")[1].strip().split(" ")[0])
            return time


def generate_result(extension, dataset, N, index_params={}, count=10):
    validate_extension(extension)

    delete_index(extension, dataset, N)

    print(get_title(extension, index_params, dataset, N))
    print_labels(f"Iteration /{count}", 'Latency (ms)', 'Disk usage')

    times = []
    disk_usages = []

    for iteration in range(count):
        time = generate_performance_result(extension, dataset, N, index_params)
        disk_usage = generate_disk_usage_result(extension, dataset, N)

        times.append(time)
        disk_usages.append(disk_usage)

        print_row(str(iteration), "{:.2f}".format(time),
                  convert_number_to_bytes(disk_usage))

        delete_index(extension, dataset, N)

    latency_average = statistics.mean(times)
    disk_usage_average = statistics.mean(disk_usages)
    if count > 1:
        latency_stddev = statistics.stdev(times)
        disk_usage_stddev = statistics.stdev(disk_usages)

    def save_create_result(metric_type, metric_value):
        save_result(
            metric_type=metric_type,
            metric_value=metric_value,
            extension=extension,
            index_params=index_params,
            dataset=dataset,
            n=convert_string_to_number(N),
        )

    save_create_result(Metric.CREATE_LATENCY, latency_average)
    save_create_result(Metric.DISK_USAGE, disk_usage_average)
    if count > 1:        
        save_create_result(Metric.CREATE_LATENCY_STDDEV, latency_stddev)
        save_create_result(Metric.DISK_USAGE_STDDEV, disk_usage_stddev)

    print('average latency:',  f"{latency_average:.2f} ms")
    if count > 1:
        print('stddev latency', f"{latency_stddev:.2f} ms")
    print('average disk usage:', convert_number_to_bytes(disk_usage_average))
    if count > 1:
        print('stddev disk usage:', convert_number_to_bytes(disk_usage_stddev))
    print()


def print_results(dataset):
    metrics = [Metric.CREATE_LATENCY, Metric.CREATE_LATENCY_STDDEV,
               Metric.DISK_USAGE, Metric.DISK_USAGE_STDDEV]
    for extension in VALID_EXTENSIONS:
        results = get_experiment_results(metrics, extension, dataset)
        if len(results) == 0:
            print(f"No results for {extension}")
        for (index_params, param_results) in results:
            print(get_title(extension, index_params, dataset))
            print_labels('N', 'Avg latency (ms)', 'Stddev latency (ms)',
                         'Avg disk usage (MB)', 'Stddev disk usage (MB)')
            for N, average_latency, stddev_latency, average_disk_usage, stddev_disk_usage in param_results:
                print_row(
                    convert_number_to_string(N),
                    "{:.2f}".format(average_latency),
                    "{:.2f}".format(stddev_latency),
                    convert_number_to_bytes(average_disk_usage),
                    convert_number_to_bytes(stddev_disk_usage),
                )
        print('\n\n')


if __name__ == '__main__':
   # Set up parser
    parser = argparse.ArgumentParser(description="benchmark create")
    cli.add_extension(parser)
    cli.add_index_params(parser)
    cli.add_dataset(parser)
    cli.add_N(parser)
    cli.add_logging(parser)
    parser.add_argument(
        '--count', type=int, default=10, help='number of iterations')

    # Parse arguments
    parsed_args = parser.parse_args()
    dataset = Dataset(parsed_args.dataset)
    extension = Extension(parsed_args.extension)
    index_params = cli.parse_index_params(extension, parsed_args)
    N = parsed_args.N or '10k'
    count = parsed_args.count
    logging.basicConfig(level=getattr(logging, parsed_args.log.upper()))

    # Generate result
    generate_result(extension, dataset, N, index_params, count=count)


def generate_cloud_result(provider, dataset, N, index_params={}, count=10):
    cloud_provider = get_cloud_provider(provider)
    index_name = get_cloud_index_name(dataset, N)
    cloud_provider.delete_index(index_name)
    index_params['name'] = index_name

    print(get_title(provider, index_params, dataset, N))
    
    print_labels(f"Iteration /{count}", 'Latency (ms)')

    times = []
    vector_data = []

    with DatabaseConnection(Extension.NONE) as conn:
        base_table_name = get_table_name(dataset=dataset, N=N)
        vector_data = conn.select(f'SELECT v FROM {base_table_name}')
        vector_data = list(map(lambda x: (str(x[0]), json.loads(x[1][0])), enumerate(vector_data)))

    for iteration in range(count):
        time = generate_cloud_performance_result(cloud_provider, vector_data, index_params)

        times.append(time)

        print_row(str(iteration), "{:.2f}".format(time))

        cloud_provider.delete_index(index_name)

    latency_average = statistics.mean(times)

    def save_create_result(metric_type, metric_value):
        save_result(
            metric_type=metric_type,
            metric_value=metric_value,
            extension=provider,
            index_params=index_params,
            dataset=dataset,
            n=convert_string_to_number(N),
        )

    save_create_result(Metric.CREATE_LATENCY, latency_average)
    if count > 1:        
        latency_stddev = statistics.stdev(times)
        save_create_result(Metric.CREATE_LATENCY_STDDEV, latency_stddev)

    print('average latency:',  f"{latency_average:.2f} ms")
    if count > 1:
        print('stddev latency', f"{latency_stddev:.2f} ms")
    print()
