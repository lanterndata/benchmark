import argparse
from .constants import VALID_DATASETS, VALID_DATASET_SIZES, VALID_EXTENSIONS, VALID_INDEX_PARAMS, SUGGESTED_K_VALUES, Extension, Dataset


def parse_args(description, args, allow_no_index=False):
    parser = argparse.ArgumentParser(description=description)

    if 'extension' in args:
        if allow_no_index:
            valid_extensions = [e.value for e in Extension]
        else:
            valid_extensions = [e.value for e in VALID_EXTENSIONS]
        parser.add_argument(
            '--extension',
            type=str, choices=valid_extensions, required=True, help='Extension type')

        params = set()
        for index, valid_index_params in VALID_INDEX_PARAMS.items():
            for param in valid_index_params:
                params.add(param)
        for param in params:
            parser.add_argument(f"--{param}", type=int, help=f"parameter for {index}")

    parser.add_argument(
        "--dataset",
        type=str, choices=[d for d in VALID_DATASETS], required=True, help="Dataset name")

    if 'N' in args:
        parser.add_argument(
            "--N",
            nargs='+', type=str, required=True, help="dataset size")
    if 'K' in args:
        parser.add_argument(
            "--K",
            nargs='+', type=int, help="K values (e.g., 5)")

    parsed_args = parser.parse_args()

    extension, N_values, K = None, None, None

    dataset = Dataset(parsed_args.dataset)
    if 'extension' in args:
        extension = Extension(parsed_args.extension)
    if 'N' in parsed_args:
        valid_datasets = VALID_DATASET_SIZES[dataset]
        N_values = parsed_args.N or valid_datasets
        if any(N not in valid_datasets for N in N_values):
            valid_sizes = ', '.join(valid_datasets)
            parser.error(
                f"Invalid dataset size(s): {', '.join(N_values)}. Valid dataset sizes for {dataset.value} are: {valid_sizes}")
    if 'K' in parsed_args:
        K = parsed_args.K or SUGGESTED_K_VALUES

    index_params = None
    if extension in VALID_INDEX_PARAMS:
        index_params = {
            param: getattr(parsed_args, param)
            for param in VALID_INDEX_PARAMS[extension] if getattr(parsed_args, param) is not None}

    return extension, index_params, dataset, N_values, K
