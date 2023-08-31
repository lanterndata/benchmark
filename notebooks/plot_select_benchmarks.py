import json
import plotly.graph_objects as go
from core.utils.process import get_experiment_results_for_params
from core.utils.plot import plot_line, plot_line_with_stddev


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