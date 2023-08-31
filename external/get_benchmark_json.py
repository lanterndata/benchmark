from .utils.get_benchmarks import get_benchmarks
from .utils import cli


if __name__ == "__main__":
    extension, index_params, dataset, N, K = cli.get_args("run benchmarks for tests or CI/CD")
    benchmarks = get_benchmarks(extension, index_params, dataset, N, K)
    benchmarks_json = {}
    for metric, value in benchmarks:
        benchmarks_json[metric.value] = value
    print(benchmarks_json)