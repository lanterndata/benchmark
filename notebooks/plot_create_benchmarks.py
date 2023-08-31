import plotly.graph_objects as go
from core.utils.constants import Metric
from core.utils.process import get_experiment_results
from core.utils.plot import plot_line_with_stddev
from core.benchmark_create import VALID_EXTENSIONS


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