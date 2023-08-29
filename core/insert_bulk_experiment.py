from .utils.cli import parse_args
from . import insert_experiment


def generate_result(extension, dataset, index_params={}):
    insert_experiment.generate_result(
        extension, dataset, index_params=index_params, bulk=True)


def print_results(dataset):
    insert_experiment.print_results(dataset, bulk=True)


def plot_results(dataset):
    insert_experiment.plot_results(dataset, bulk=True)


if __name__ == '__main__':
    extension, index_params, dataset, _, _ = parse_args(
        "insert bulk experiment", ['extension'], allow_no_index=True)
    generate_result(extension, dataset, index_params)
