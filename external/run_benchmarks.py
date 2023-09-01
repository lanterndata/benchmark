from core.utils.delete_index import delete_index
from core.utils.process import save_result
from core.utils.numbers import convert_string_to_number
from core.utils.constants import Extension, Metric
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
    tps_response, latency_average_response, latency_stddev_response = benchmark_select.generate_performance_result(
        extension, dataset, N, K, bulk=True)
    recall_response = benchmark_select.generate_recall_result(
        extension, dataset, N, K)
    shared_hit_response, shared_hit_stddev_response, read_response, read_stddev_response = benchmark_select.generate_utilization_result(
        extension, dataset, N, K, bulk=True)
    delete_index(extension, dataset, N)

    save_result(Metric.CREATE_LATENCY, latency_create, **create_kwargs)
    save_result(Metric.DISK_USAGE, disk_usage, **create_kwargs)
    save_result(**tps_response, **select_kwargs)
    save_result(**latency_average_response, **select_kwargs)
    save_result(**latency_stddev_response, **select_kwargs)
    save_result(**recall_response, **select_kwargs)
    save_result(**shared_hit_response, **select_kwargs)
    save_result(**shared_hit_stddev_response, **select_kwargs)
    save_result(**read_response, **select_kwargs)
    save_result(**read_stddev_response, **select_kwargs)

    benchmark_insert.generate_result(
        extension, dataset, N, index_params, bulk=True)
