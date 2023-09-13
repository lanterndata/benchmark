import json
import plotly.graph_objects as go
from core.utils.constants import Metric
from core.utils.process import get_experiment_results_for_params
from core.utils.plot import plot_line_with_stddev, plot_bar


def plot_latency_results(configuration, dataset, plot_type = 'line'):
    fig = go.Figure()
    
    metric_types = [Metric.CREATE_LATENCY, Metric.CREATE_LATENCY_STDDEV]
    for extension, index_params_list in configuration.items():
        for index, index_params in enumerate(index_params_list):
            results = get_experiment_results_for_params(metric_types, extension, json.dumps(index_params), dataset)
            if len(results) == 0:
                continue
            N_values, averages, stddevs = zip(*results)

            if plot_type == 'bar':
                plot_bar(fig, extension, index_params, N_values, averages, index=index)
            else:
                plot_line_with_stddev(
                    fig, extension, index_params, N_values, averages, stddevs, index=index)

    fig.update_layout(
        title=f"Create Index Latency over Number of Rows for {dataset.value}",
        xaxis=dict(title='Number of rows'),
        yaxis=dict(title='Latency (ms)'),
    )
    fig.show()


def plot_disk_usage_results(configuration, dataset, plot_type = 'line'):
    fig = go.Figure()
    metric_types = [Metric.DISK_USAGE, Metric.DISK_USAGE_STDDEV]
    for extension, index_params_list in configuration.items():
        for index, index_params in enumerate(index_params_list):
            results = get_experiment_results_for_params(metric_types, extension, json.dumps(index_params), dataset)
            if len(results) == 0:
                continue
            N_values, averages, stddevs = zip(*results)
            if plot_type == 'bar':
                plot_bar(fig, extension, index_params, N_values, averages, index=index)
            else:
                plot_line_with_stddev(
                    fig, extension, index_params, N_values, averages, stddevs, index=index)
    fig.update_layout(
        title=f"Disk Usage over Number of Rows for {dataset.value}",
        xaxis=dict(title='Number of rows'),
        yaxis=dict(title='Disk Usage (bytes)'),
    )
    fig.show()