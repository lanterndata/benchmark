from .utils.constants import Extension, Metric
from .utils import cli
from .utils.process import get_experiment_result
import argparse

if __name__ == '__main__':
    # Set up parser
    parser = argparse.ArgumentParser(description="retrieve benchmarking metric")
    cli.add_extension(parser)
    cli.add_index_params(parser)
    cli.add_dataset(parser)
    cli.add_N(parser)
    cli.add_K(parser)
    metric_choices = [m.key for m in Metric]
    parser.add_argument("--metric", choices=metric_choices, required=True, help="metric to retrieve")

    # Parse arguments
    parsed_args = parser.parse_args()
    extension = Extension(parsed_args.extension)
    index_params = cli.parse_index_params(extension, parsed_args)
    dataset = parsed_args.dataset
    N = parsed_args.N
    cli.validate_N(parser, dataset, N)
    K = parsed_args.K
    metric = Metric[parsed_args.metric]

    # Retrieve and print result
    result = get_experiment_result(metric, extension, index_params, dataset, N, K)
    print(result)