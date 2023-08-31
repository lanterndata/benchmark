from typing import List, Tuple
from core.utils.constants import Metric
from external.utils import cli
from external.utils.get_benchmarks import get_benchmarks


def print_benchmarks(benchmarks: List[Tuple[Metric, str, str]]):
    divider_length = 70
    divider_line = "-" * divider_length

    print(divider_line)
    print("| %-20s | %20s | %20s |" % ("metric", "old", "new"))
    print(divider_line)

    for metric, old_value, new_value in benchmarks:
        display_old_value = old_value if old_value is not None else "-"
        data = (metric.value, display_old_value, new_value)
        print("| %-20s | %20s | %20s |" % data)
    print(divider_line)


if __name__ == "__main__":
    extension, index_params, dataset, N, K = cli.get_args(
        "show benchmark results for tests or CI/CD")
    benchmarks = get_benchmarks(
        extension, index_params, dataset, N, K, return_old=True)
    print_benchmarks(benchmarks)
