from typing import List, Tuple
from core.utils.constants import Metric
from external.utils import cli
from external.utils.get_benchmarks import get_benchmarks


def print_benchmarks(benchmarks: List[Tuple[Metric, str, str]]):
    divider_length = 80
    divider_line = "-" * divider_length

    print(divider_line)
    print("| %-21s | %18s | %18s | %10s |" %
          ("metric", "old", "new", "pct change"))
    print(divider_line)

    for metric, old_value, new_value in benchmarks:
        display_old_value = "-" if old_value is None else \
            "%.3f" % float(old_value)
        display_new_value = "-" if new_value is None else \
            "%.3f" % float(new_value)
        pct_change = "-" if new_value is None or old_value is None else \
            (float(new_value) - float(old_value)) / float(old_value) * 100
        display_pct_change = "%.2f%%" % pct_change
        data = (metric.value, display_old_value,
                display_new_value, display_pct_change)
        print("| %-21s | %18s | %18s | %10s |" % data)

    print(divider_line)


if __name__ == "__main__":
    extension, index_params, dataset, N, K = cli.get_args(
        "show benchmark results for tests or CI/CD")
    benchmarks = get_benchmarks(
        extension, index_params, dataset, N, K, return_old=True)
    print_benchmarks(benchmarks)
