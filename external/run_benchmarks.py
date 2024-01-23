from core.utils.delete_index import delete_index
from core.utils.process import save_result
from core.utils.numbers import convert_string_to_number
from core.utils.constants import Extension, Metric, Dataset
from core import benchmark_create, benchmark_insert, benchmark_select
from external.utils import cli

if __name__ == "__main__":
    extension, index_params, dataset, N, K = cli.get_args(
        "run benchmarks for tests or CI/CD")

    assert extension != Extension.NONE

    create_kwargs = {
        'extension': extension,
        'index_params': index_params,
        'dataset': dataset,
        'n': convert_string_to_number(N),
    }
    select_kwargs = {
        **create_kwargs,
        'k': K,
    }

    delete_index(extension, dataset, N)
    latency_create = benchmark_create.generate_performance_result(
        extension, dataset, N, index_params)
    disk_usage = benchmark_create.generate_disk_usage_result(
        extension, dataset, N)
    benchmark_select.generate_result(
        extension, dataset, N, [K], index_params, bulk=True, skip_index=True)
    benchmark_select.generate_result(
        extension, dataset, N, [K], index_params, bulk=False, skip_index=True)
    delete_index(extension, dataset, N)
    save_result(Metric.CREATE_LATENCY, latency_create, **create_kwargs)
    save_result(Metric.DISK_USAGE, disk_usage, **create_kwargs)

    benchmark_insert.generate_result(
        extension, dataset, N, index_params, K=None, bulk=False, max_N=10000)
