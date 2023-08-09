import argparse
from scripts.script_utils import VALID_DATASETS, VALID_EXTENSIONS_AND_NONE
import insert_experiment

def generate_result(extension, dataset):
    insert_experiment.generate_result(extension, dataset, bulk=True)

def print_results(dataset):
    insert_experiment.print_results(dataset, bulk=True)

def plot_results(dataset):
    insert_experiment.plot_results(dataset, bulk=True)

if __name__ == '__main__':
    extension, index_params, dataset, _, _ = parse_args("insert bulk experiment", ['extension'])
    generate_result(extension, dataset, index_params)