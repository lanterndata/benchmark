from core import benchmark_create, benchmark_insert, benchmark_select
from external.utils import cli

if __name__ == "__main__":
    extension, index_params, dataset, N, K = cli.get_args(
        "run benchmarks for tests or CI/CD")
    benchmark_create.generate_result(
        extension, dataset, N, index_params, count=1)
    benchmark_insert.generate_result(extension, dataset, N, index_params)
    benchmark_select.generate_result(extension, dataset, N, [K], index_params)
