from .utils.constants import Extension, Metric
from .utils.cli import add_extension, add_index_params, parse_index_params, add_dataset, add_N, add_K, validate_N_values
from .utils.process import get_experiment_result
import argparse

if __name__ == '__main__':
    # Set up parser
    parser = argparse.ArgumentParser(description="retrieve benchmarking metric")
    add_extension(parser)
    add_index_params(parser)
    add_dataset(parser)
    add_N(parser)
    add_K(parser)
    metric_choices = [m.key for m in Metric]
    parser.add_argument("--metric", choices=metric_choices, required=True, help="metric to retrieve")

    # Parse arguments
    parsed_args = parser.parse_args()
    extension = Extension(parsed_args.extension)
    index_params = parse_index_params(extension, parsed_args)
    dataset = parsed_args.dataset
    N = parsed_args.N
    validate_N_values(parser, dataset, [N])
    K = parsed_args.K
    metric = Metric[parsed_args.metric]

    # Retrieve and print result
    result = get_experiment_result(metric, extension, index_params, dataset, N, K)
    print(result)