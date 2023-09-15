import logging
from typing import Dict
from .constants import VALID_DATASETS, VALID_DATASET_SIZES, VALID_INDEX_PARAMS, Extension

def add_logging(parser):
    parser.add_argument("--log", default="WARNING", help="Logging level", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])


def add_dataset(parser):
    choices = [d for d in VALID_DATASETS]
    parser.add_argument("--dataset", type=str, choices=choices,
                        required=True, help="Dataset name")


def add_N(parser):
    parser.add_argument("--N",
                        type=str, required=True, help="dataset size")


def add_K(parser):
    parser.add_argument("--K", type=int, help="K values (e.g., 5)")


def add_K_values(parser):
    parser.add_argument("--K", nargs='+', type=int, help="K values (e.g., 5)")


def add_extension(parser, allow_no_index=False):
    if allow_no_index:
        choices = [e.value for e in Extension]
    else:
        choices = [e.value for e in Extension if e != Extension.NONE]
    parser.add_argument(
        '--extension',
        type=str, choices=choices, required=True, help='Extension type')


def add_index_params(parser):
    params = set()
    for index, valid_index_params in VALID_INDEX_PARAMS.items():
        for param in valid_index_params:
            params.add(param)
    for param in params:
        parser.add_argument(f"--{param}", type=int,
                            help=f"parameter for {index}")


def validate_N_values(parser, dataset, N_values):
    valid_dataset_sizes = VALID_DATASET_SIZES[dataset]
    if any(N not in valid_dataset_sizes for N in N_values):
        parser.error(
            f"Invalid dataset size(s): {', '.join(N_values)}. " +
            f"Valid dataset sizes for {dataset.value} are: {', '.join(valid_dataset_sizes)}"
        )


def validate_N(parser, dataset, N):
    validate_N_values(parser, dataset, [N])


def parse_index_params(extension: Extension, parsed_args: Dict[str, int]):
    index_params = {}
    if extension in VALID_INDEX_PARAMS:
        index_params = {
            param: getattr(parsed_args, param)
            for param in VALID_INDEX_PARAMS[extension] if getattr(parsed_args, param) is not None}
    return index_params