from utils.cli import parse_args
from utils.constants import Metric
from . import select_experiment


def generate_result(extension, dataset, N, K_values, index_params={}):
    select_experiment.generate_result(
        extension, dataset, N, K_values, index_params=index_params, bulk=True)


def run_hyperparameter_search(extension, dataset, N):
    select_experiment.run_hyperparameter_search(
        extension, dataset, N, bulk=True)


def plot_hyperparameter_search(extensions, dataset, N, xaxis=Metric.RECALL, yaxis=Metric.SELECT_BULK_LATENCY):
    select_experiment.plot_hyperparameter_search(
        extensions, dataset, N, xaxis, yaxis)


if __name__ == '__main__':
    extension, index_params, dataset, _, _ = parse_args(
        "select bulk experiment", ['extension'])
    generate_result(extension, dataset, index_params)
