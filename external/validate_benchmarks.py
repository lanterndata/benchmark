import sys
import math
from typing import List, Tuple
from core.utils.constants import Metric, METRICS_THAT_SHOULD_DECREASE, METRICS_THAT_SHOULD_INCREASE
from external.utils.get_benchmarks import get_benchmarks
from external.utils import cli


def validate_benchmarks(benchmarks: List[Tuple[Metric, str, str]]):
    warnings = []
    errors = []

    for metric, old_value, new_value in benchmarks:
        if old_value is None or new_value is None:
            continue

        diff = new_value - old_value
        pct_change = diff / old_value

        if metric == Metric.RECALL:
            if diff < -0.05:
                errors.append(f"Recall decreased by {diff:2f}")
            elif diff < 0:
                warnings.append(f"Recall decreased by {diff:2f}")
            elif new_value >= 1.0:
                errors.append(f"Recall is 1.0")
        if metric in METRICS_THAT_SHOULD_INCREASE:
            if pct_change < 0.1:
                errors.append(
                    f"{metric.value} decreased by {pct_change * 100:.2f}%")
            elif pct_change < 0:
                warnings.append(
                    f"{metric.value} decreased by {pct_change * 100:.2f}%")
        elif metric in METRICS_THAT_SHOULD_DECREASE:
            if pct_change > 0.1:
                errors.append(
                    f"{metric.value} increased by {pct_change * 100:.2f}%")
            elif pct_change > 0:
                warnings.append(
                    f"{metric.value} increased by {pct_change * 100:.2f}%")

    for warning in warnings:
        print('WARNING:', warning)
    for error in errors:
        print('ERROR:', error)
    if len(errors) > 0:
        sys.exit(1)


if __name__ == "__main__":
    extension, index_params, dataset, N, K = cli.get_args(
        "validate benchmark results for tests or CI/CD")
    benchmarks = get_benchmarks(
        extension, index_params, dataset, N, K, return_old=True)
    validate_benchmarks(benchmarks)
