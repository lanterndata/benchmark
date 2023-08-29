import subprocess
import statistics
import plotly.graph_objects as go
from .utils.database import DatabaseConnection, get_database_url
from .utils.delete_index import delete_index
from .utils.create_index import get_create_index_query, get_index_name
from .utils.numbers import convert_string_to_number, convert_number_to_string, convert_number_to_bytes
from .utils.constants import Metric, VALID_EXTENSIONS
from .utils.cli import parse_args
from .utils.process import save_result, get_experiment_results
from .utils.print import print_labels, print_row, get_title
from .utils.plot import plot_line_with_stddev

SUPPRESS_COMMAND = "SET client_min_messages TO WARNING"


def generate_disk_usage_result(extension, dataset, N):
    index = get_index_name(dataset, N)
    sql = f"SELECT pg_total_relation_size('{index}')"
    with DatabaseConnection(extension) as conn:
        disk_usage = conn.select_one(sql)[0]
    return disk_usage


def generate_performance_result(extension, dataset, N, index_params):
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
    latency_stddev = statistics.stdev(times)
    disk_usage_average = statistics.mean(disk_usages)
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
    save_create_result(Metric.CREATE_LATENCY_STDDEV, latency_stddev)
    save_create_result(Metric.DISK_USAGE, disk_usage_average)
    save_create_result(Metric.DISK_USAGE_STDDEV, disk_usage_stddev)

    print('average latency:',  f"{latency_average:.2f} ms")
    print('stddev latency', f"{latency_stddev:.2f} ms")
    print('average disk usage:', convert_number_to_bytes(disk_usage_average))
    print('stddev disk usage:', convert_number_to_bytes(disk_usage_stddev))
    print()

    delete_index(extension, dataset, N)


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


def plot_latency_results(dataset):
    fig = go.Figure()
    metric_types = [Metric.CREATE_LATENCY, Metric.CREATE_LATENCY_STDDEV]
    for extension in VALID_EXTENSIONS:
        results = get_experiment_results(metric_types, extension, dataset)
        for index, (index_params, param_results) in enumerate(results):
            N_values, averages, stddevs = zip(*param_results)
            plot_line_with_stddev(
                fig, extension, index_params, N_values, averages, stddevs, index=index)
    fig.update_layout(
        title=f"Create Index Latency over Number of Rows for {dataset.value}",
        xaxis=dict(title='Number of rows'),
        yaxis=dict(title='Latency (ms)'),
    )
    fig.show()


def plot_disk_usage_results(dataset):
    fig = go.Figure()
    metric_types = [Metric.DISK_USAGE, Metric.DISK_USAGE_STDDEV]
    for extension in VALID_EXTENSIONS:
        results = get_experiment_results(metric_types, extension, dataset)
        for index, (index_params, param_results) in enumerate(results):
            N_values, averages, stddevs = zip(*param_results)
            plot_line_with_stddev(
                fig, extension, index_params, N_values, averages, stddevs, index=index)
    fig.update_layout(
        title=f"Disk Usage over Number of Rows for {dataset.value}",
        xaxis=dict(title='Number of rows'),
        yaxis=dict(title='Disk Usage (bytes)'),
    )
    fig.show()


if __name__ == '__main__':
    extension, index_params, dataset, N_values, _ = parse_args(
        "create experiment", ['extension', 'N'])
    for N in N_values:
        generate_result(extension, dataset, N, index_params)
