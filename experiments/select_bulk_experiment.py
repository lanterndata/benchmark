from scripts.script_utils import parse_args
import select_experiment


def generate_result(extension, dataset, N, K_values, index_params={}):
    select_experiment.generate_result(
        extension, dataset, N, K_values, index_params=index_params, bulk=True)


def plot_results(dataset):
    select_experiment.plot_results(dataset, bulk=True)


if __name__ == '__main__':
    extension, index_params, dataset, _, _ = parse_args(
        "select bulk experiment", ['extension'])
    generate_result(extension, dataset, index_params)
