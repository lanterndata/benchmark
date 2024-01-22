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


def get_corresponding_stddev_result(metric_name, benchmarks):
    metric_name_without_unit = metric_name.split("(")[0].strip()
    for result in benchmarks:
        metric = result[0].value

        if metric_name_without_unit in metric and "stddev" in metric:
            return result

    return None

def get_metric_name(metric_name: str, bulk_size: int):
    if "bulk" not in metric_name:
        return metric_name

    return metric_name.replace("bulk", "bulk({})".format(bulk_size))

def print_benchmarks(benchmarks: List[Tuple[Metric, str, str]], markdown=False):
    divider_length = 96
    divider_line = "-" * divider_length

    if markdown:
        print("# Benchmarks")
    else:
        print(divider_line)
    print("| %-31s | %20s | %20s | %12s |" %
          ("metric", "old", "new", "pct change"))
    print(f"|{33 * '-'}|{22 * '-'}|{22 * '-'}|{14 * '-'}|")

    for metric, old_value, new_value in benchmarks:
        # Do not show stddev values
        if "stddev" in metric.value:
            continue

        stddev_result = get_corresponding_stddev_result(metric.value, benchmarks)
        stddev_result_new = ""
        stddev_result_old = ""

        if stddev_result and stddev_result[1]:
            stddev_result_old = " ± %.3f𝜎" % stddev_result[1]

        if stddev_result and stddev_result[2]:
            stddev_result_new = " ± %.3f𝜎" % stddev_result[2]


        display_old_value = "-" if old_value is None else \
            "%.3f%s" % (old_value, stddev_result_old)
        display_new_value = "-" if new_value is None else \
            "%.3f%s" % (new_value, stddev_result_new)
        has_no_change = new_value is None or old_value is None or old_value == new_value
        if has_no_change:
            display_pct_change = "-"
        else:
            pct_change = (new_value - old_value) / old_value * 100
            display_pct_change = "%.2f%%" % pct_change
            if pct_change > 0:
                display_pct_change = "+" + display_pct_change

        metric_name = get_metric_name(metric.value, 100)
        data = (metric_name, display_old_value,
                display_new_value, display_pct_change)
        print("| %-31s | %20s | %20s | %12s |" % data)

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
