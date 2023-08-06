import argparse
from scripts.script_utils import VALID_DATASETS, VALID_EXTENSIONS_AND_NONE
import insert_experiment

def generate_result(extension, dataset):
    insert_experiment.generate_result(extension, dataset, bulk=True)

def plot_results(dataset):
    insert_experiment.plot_results(dataset, bulk=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="insert experiment")
    parser.add_argument("--dataset", type=str, choices=VALID_DATASETS.keys(), required=True, help="output file name (required)")
    parser.add_argument('--extension', type=str, choices=VALID_EXTENSIONS_AND_NONE, required=True, help='extension type')
    args = parser.parse_args()
    
    extension = args.extension
    dataset = args.dataset

    generate_result(extension, dataset)