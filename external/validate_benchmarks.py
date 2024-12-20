import sys
import logging
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
        pct_change = diff / (old_value or 1)

        if metric in METRICS_THAT_SHOULD_INCREASE:
            if pct_change < -0.1:
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
        logging.warning(warning)
    for error in errors:
        logging.error(error)
    if len(errors) > 0:
        sys.exit(1)


if __name__ == "__main__":
    extension, index_params, dataset, N, K = cli.get_args(
        "validate benchmark results for tests or CI/CD")
    benchmarks = get_benchmarks(
        extension, index_params, dataset, N, K, return_old=True)
    validate_benchmarks(benchmarks)
