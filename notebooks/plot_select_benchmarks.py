import json
import plotly.graph_objects as go
from core.utils.process import get_experiment_results_for_params
from core.utils.plot import plot_line, plot_line_with_stddev, plot_bar


# Given a mapping of extension to index_params and fixed parameter, support plotting latency vs. variable parameter
def generate_plot(configuration, dataset, fixed_param, fixed_param_value, variable_param, metric_type, metric_stddev_type=None, plot_type = 'line'):
    fig = go.Figure()
    for extension, index_params_list in configuration.items():
        for index, index_params in enumerate(index_params_list):
            metric_types = [
                metric_type, metric_stddev_type] if metric_stddev_type is not None else [metric_type]
            results = get_experiment_results_for_params(
                metric_types, extension, json.dumps(index_params), dataset, **{(fixed_param.value.upper()): fixed_param_value})
            if len(results) == 0:
                continue
            if metric_stddev_type is not None:
                param_values, metric_values, metric_stddev_values = zip(*results)
                if plot_type == 'bar':
                    plot_bar(fig, extension, index_params,
                            param_values, metric_values, index=index)
                else:
                    plot_line_with_stddev(fig, extension, index_params,
                                    param_values, metric_values, metric_stddev_values, index=index)
            else:
                param_values, metric_values = zip(*results)
                plot_trace = plot_line if plot_type == 'line' else plot_bar
                plot_trace(fig, extension, index_params,
                        param_values, metric_values, index=index)
    
    variable_param_value = variable_param.value
    if variable_param_value == 'n':
        variable_param_value = 'number of rows'
    fig.update_layout(
        title=f"{metric_type.value} vs. {variable_param_value} ({dataset.value}, {fixed_param.value.upper()}={fixed_param_value})",
        xaxis_title=variable_param_value,
        yaxis_title=metric_type.value,
    )
    fig.show()