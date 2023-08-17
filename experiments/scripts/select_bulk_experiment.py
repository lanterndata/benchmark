from utils.cli import parse_args
from . import select_experiment


def generate_result(extension, dataset, N, K_values, index_params={}):
    select_experiment.generate_result(
        extension, dataset, N, K_values, index_params=index_params, bulk=True)


def generate_plot(configuration, dataset, fixed_param, fixed_param_value, variable_param, metric_type, metric_stddev_type=None):
    select_experiment.generate_plot(
        configuration, dataset, fixed_param, fixed_param_value, variable_param, metric_type, metric_stddev_type=metric_stddev_type)


if __name__ == '__main__':
    extension, index_params, dataset, _, _ = parse_args(
        "select bulk experiment", ['extension'])
    generate_result(extension, dataset, index_params)
