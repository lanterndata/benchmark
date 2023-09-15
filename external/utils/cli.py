import argparse
from typing import Optional, Callable, List
from core.utils.constants import Extension, Dataset
from core.utils import cli


def get_args(description, add_arguments: Optional[Callable[[argparse.ArgumentParser], None]] = None, additional_args: List[str] = []):
    # Set up parser
    parser = argparse.ArgumentParser(description=description)
    cli.add_extension(parser)
    cli.add_index_params(parser)
    cli.add_dataset(parser)
    cli.add_N(parser)
    cli.add_K(parser)
    if add_arguments is not None:
        add_arguments(parser)

    # Parse arguments
    parsed_args = parser.parse_args()
    extension = Extension(parsed_args.extension)
    index_params = cli.parse_index_params(extension, parsed_args)
    dataset = Dataset(parsed_args.dataset)
    N = parsed_args.N
    cli.validate_N(parser, dataset, N)
    K = parsed_args.K
    logging.basicConfig(level=getattr(logging, parsed_args.log.upper()))

    return extension, index_params, dataset, N, K, *[getattr(parsed_args, arg) for arg in additional_args]
