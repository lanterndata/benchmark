import sys
from typing import List, Tuple
from core.utils.constants import Metric
from .get_benchmarks import get_benchmarks
from . import cli


def validate_benchmarks(benchmarks: List[Tuple[Metric, str, str]]):
    warnings = []
    errors = []

    for metric, old_value, new_value in benchmarks:
        metric,        
        if metric == Metric.RECALL:
            recall_difference = new_value - old_value
            if recall_difference < -0.05:
                errors.append(f"Recall decreased by {recall_difference:2f}")
            elif recall_difference < 0:
                warnings.append(f"Recall decreased by {recall_difference:2f}")
            elif new_value >= 1.0:
                errors.append(f"Recall is 1.0")

    for warning in warnings:
        print('WARNING:', warning)
    for error in errors:
        print('ERROR:', error)
    if len(errors) > 0:
        sys.exit(1)


if __name__ == "__main__":
    extension, index_params, dataset, N, K = cli.get_args("validate benchmark results for tests or CI/CD")
    benchmarks = get_benchmarks(extension, index_params, dataset, N, K, return_old=True)
    validate_benchmarks(benchmarks)
