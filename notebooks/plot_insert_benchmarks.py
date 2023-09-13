import plotly.graph_objects as go
from core.benchmark_insert import get_tps_metric, get_latency_metric, get_latency_stddev_metric
from core.utils.constants import Extension
from core.utils.process import get_experiment_results
from core.utils.plot import plot_line_with_stddev, plot_line, plot_bar



def plot_results(dataset, plot_type='line', bulk=False):
    metric_tuples = [
        ('transactions per second', get_tps_metric(bulk)),
        ('latency (ms)', (get_latency_metric(bulk), get_latency_stddev_metric(bulk)))
    ]
    for yaxis_title, metric_type in metric_tuples:
        fig = go.Figure()
        for extension in Extension:
            results = get_experiment_results(metric_type, extension, dataset)
            for index, (index_params, param_results) in enumerate(results):
                if isinstance(metric_type, tuple):
                    x_values, y_means, y_stddevs = zip(*param_results)
                    if plot_type == 'bar':
                        plot_bar(fig, extension, index_params, x_values, y_means, index=index)
                    else:
                        plot_line_with_stddev(
                            fig, extension, index_params, x_values, y_means, y_stddevs, index=index)
                else:
                    x_values, y_values = zip(*param_results)
                    plot_trace = plot_bar if plot_type == 'bar' else plot_line
                    plot_trace(fig, extension, index_params,
                              x_values, y_values, index=index)
        if isinstance(metric_type, tuple):
            plot_title = f"{dataset.value} - {metric_type[0].value}"
        else:
            plot_title = f"{dataset.value} - {metric_type.value}"
        fig.update_layout(
            title=plot_title,
            xaxis_title=f"number of rows inserted",
            yaxis_title=yaxis_title,
        )
        fig.show()