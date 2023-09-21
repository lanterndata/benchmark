import argparse
import logging
from typing import List, Tuple
from core.utils.constants import Metric
from external.utils import cli
from external.utils.get_benchmarks import get_benchmarks


def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('--markdown', action='store_true',
                        help='Print benchmarks in markdown format')
    parser.add_argument('--loginfo', action='store_true', help='Print logs')


def print_benchmarks(benchmarks: List[Tuple[Metric, str, str]], markdown=False):
    divider_length = 90
    divider_line = "-" * divider_length

    if markdown:
        print("# Benchmarks")
    else:
        print(divider_line)
    print("| %-31s | %18s | %18s | %10s |" %
          ("metric", "old", "new", "pct change"))
    print(f"|{33 * '-'}|{20 * '-'}|{20 * '-'}|{12 * '-'}|")

    for metric, old_value, new_value in benchmarks:
        display_old_value = "-" if old_value is None else \
            "%.3f" % old_value
        display_new_value = "-" if new_value is None else \
            "%.3f" % new_value
        has_no_change = new_value is None or old_value is None or old_value == new_value
        if has_no_change:
            display_pct_change = "-"
        else:
            pct_change = (new_value - old_value) / old_value * 100
            display_pct_change = "%.2f%%" % pct_change
            if pct_change > 0:
                display_pct_change = "+" + display_pct_change
        data = (metric.value, display_old_value,
                display_new_value, display_pct_change)
        print("| %-31s | %18s | %18s | %10s |" % data)

    if not markdown:
        print(divider_line)


if __name__ == "__main__":
    extension, index_params, dataset, N, K, markdown, loginfo = cli.get_args(
        "show benchmark results for tests or CI/CD", add_arguments, ['markdown', 'loginfo'])
    if loginfo:
        logging.basicConfig(level=logging.INFO)
    benchmarks = get_benchmarks(
        extension, index_params, dataset, N, K, return_old=True)
    print_benchmarks(benchmarks, markdown=markdown)
