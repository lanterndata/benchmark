import argparse
from core.utils.constants import Extension, Dataset
from core.utils import cli

def get_args(descrption):
    # Set up parser
    parser = argparse.ArgumentParser(description=descrption)
    cli.add_extension(parser)
    cli.add_index_params(parser)
    cli.add_dataset(parser)
    cli.add_N(parser)
    cli.add_K(parser)

    # Parse arguments
    parsed_args = parser.parse_args()
    extension = Extension(parsed_args.extension)
    index_params = cli.parse_index_params(extension, parsed_args)
    dataset = Dataset(parsed_args.dataset)
    N = parsed_args.N
    cli.validate_N(parser, dataset, N)
    K = parsed_args.K

    return extension, index_params, dataset, N, K