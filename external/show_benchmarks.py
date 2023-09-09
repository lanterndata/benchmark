import argparse
from typing import List, Tuple
from core.utils.constants import Metric
from external.utils import cli
from external.utils.get_benchmarks import get_benchmarks


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """
    Add specific arguments for the show_benchmarks script.
    """
    parser.add_argument('--markdown', action='store_true',
                        help='Print benchmarks in markdown format')


def print_benchmarks(benchmarks: List[Tuple[Metric, str, str]], markdown=False):
    divider_length = 80
    divider_line = "-" * divider_length

    if markdown:
        print("# Benchmarks")
    else:
        print(divider_line)
    print("| %-21s | %18s | %18s | %10s |" %
          ("metric", "old", "new", "pct change"))
    print(divider_line)

    for metric, old_value, new_value in benchmarks:
        display_old_value = "-" if old_value is None else \
            "%.3f" % float(old_value)
        display_new_value = "-" if new_value is None else \
            "%.3f" % float(new_value)
        display_pct_change = "-" if new_value is None or old_value is None else \
            "%.2f%%" % (float(new_value) - float(old_value)) / \
            float(old_value) * 100
        data = (metric.value, display_old_value,
                display_new_value, display_pct_change)
        print("| %-21s | %18s | %18s | %10s |" % data)

    if not markdown:
        print(divider_line)


if __name__ == "__main__":
    extension, index_params, dataset, N, K, markdown = cli.get_args(
        "show benchmark results for tests or CI/CD", add_arguments, ['markdown'])
    benchmarks = get_benchmarks(
        extension, index_params, dataset, N, K, return_old=True)
    print_benchmarks(benchmarks, markdown=markdown)
