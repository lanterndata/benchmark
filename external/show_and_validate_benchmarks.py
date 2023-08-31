import sys
from typing import List, Tuple
from core.utils.constants import Metric
from core.utils.process import get_experiment_result
from . import cli


def print_metrics(metrics: List[Tuple[str, str, str]]):
    divider_length = 70
    divider_line = "-" * divider_length

    print(divider_line)
    print("| %-20s | %20s | %20s |" % ("metric", "old", "new"))
    print(divider_line)

    for name, old_value, new_value in metrics:
        print("| %-20s | %20s | %20s |" % (name, old_value, new_value))
    print(divider_line)


def main(extension, index_params, dataset, N, K):
    metrics_to_print = []
    warnings = []
    errors = []

    new_recall = get_experiment_result(Metric.RECALL, extension, index_params, dataset, N, K)
    old_recall = 0.0  # TODO
    metrics_to_print.append((Metric.RECALL.value, old_recall, new_recall))
    recall_difference = new_recall - old_recall
    if recall_difference < -0.05:
        errors.append(f"Recall decreased by {recall_difference:2f}")
    elif recall_difference < 0:
        warnings.append(f"WARNING: Recall decreased by {recall_difference:2f}")
    elif new_recall >= 1.0:
        errors.append(f"ERROR: Recall is 1.0")

    print_metrics(metrics_to_print)

    for warning in warnings:
        print('WARNING:', warning)
    for error in errors:
        print('ERROR:', error)
    if len(errors) > 0:
        sys.exit(1)


if __name__ == "__main__":
    extension, index_params, dataset, N, K = cli.get_args("show and validate benchmark results for tests or CI/CD")
    main(extension, index_params, dataset, N, K)
