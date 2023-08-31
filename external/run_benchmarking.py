import sys
import argparse
from typing import List, Tuple
from core import benchmark_create, benchmark_insert, benchmark_select
from core.utils.constants import Extension, Metric, Dataset
from core.utils.process import get_experiment_result
from core.utils import cli


def run_benchmarks(extension, index_params, dataset, N, K):
    benchmark_create.generate_result(extension, dataset, N, index_params)
    benchmark_insert.generate_result(extension, dataset, N, index_params)
    benchmark_select.generate_result(extension, dataset, N, [K], index_params)


def print_metrics(metrics: List[Tuple[str, str, str]]):
    divider_length = 70
    divider_line = "-" * divider_length

    print(divider_line)
    print("| %-20s | %20s | %20s |" % ("metric", "old", "new"))
    print(divider_line)

    for name, old_value, new_value in metrics:
        print("| %-20s | %20s | %20s |" % (name, old_value, new_value))
    print(divider_line)


def print_errors_and_warnings(messages: List[str]):
    error = False
    for message in messages:
        print(message)
        if "ERROR" in message:
            error = True
    if error:
        sys.exit(1)


def main(extension, index_params, dataset, N, K):
    run_benchmarks(extension, index_params, dataset, N, K)

    metrics_to_print = []
    errors_and_warnings = []

    # Recall
    new_recall = get_experiment_result(Metric.RECALL, extension, index_params, dataset, N, K)
    old_recall = 0.0  # TODO
    metrics_to_print.append((Metric.RECALL.value, old_recall, new_recall))
    recall_difference = new_recall - old_recall
    if recall_difference < -0.05:
        errors_and_warnings.append(f"ERROR: Recall decreased by {recall_difference:2f}")
    elif recall_difference < 0:
        errors_and_warnings.append(f"WARNING: Recall decreased by {recall_difference:2f}")
    elif new_recall >= 1.0:
        errors_and_warnings.append(f"ERROR: Recall is 1.0")

    print_metrics(metrics_to_print)
    print_errors_and_warnings(errors_and_warnings)


if __name__ == "__main__":
    # Set up parser
    parser = argparse.ArgumentParser(
        description="run benchmarking for tests or CI/CD")
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

    # Run benchmarks
    main(extension, index_params, dataset, N, K)
