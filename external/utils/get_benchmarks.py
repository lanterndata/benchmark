import os
import json
from github import Github
from core.utils.constants import Metric
from core.utils.process import get_experiment_result
import zipfile

REPO_NAME = 'lanterndata/lanterndb'
BASE_REF = os.environ.get('GITHUB_BASE_REF', 'main')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', None)


def get_old_benchmarks():
    if not GITHUB_TOKEN:
        return {}
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    artifact = None
    workflows = repo.get_workflow_runs(branch=BASE_REF)
    for workflow in workflows:
        for artifact_ in workflow.artifacts():
            if artifact_.name == "benchmark-results":
                artifact = artifact_
                break
        if artifact:
            break
    if artifact:
        artifact_file_name = "/tmp/benchmark-results-artifact.zip"
        artifact.download_as_zip(artifact_file_name)
        with zipfile.ZipFile(artifact_file_name, 'r') as zip_ref:
            zip_ref.extractall("/tmp")
        with open("/tmp/benchmarks-out.json", "r") as f:
            data = json.load(f)
        return data
    return {}


def get_benchmarks(extension, index_params, dataset, N, K, return_old=False):
    benchmarks = []

    def add_metric(metric_type, use_K=False):
        new_metric = get_experiment_result(
            metric_type, extension, index_params, dataset, N, K=K if use_K else 0)
        benchmarks.append((metric_type, new_metric))

    add_metric(Metric.RECALL, use_K=True)
    add_metric(Metric.SELECT_TPS, use_K=True)
    add_metric(Metric.SELECT_LATENCY, use_K=True)
    add_metric(Metric.CREATE_LATENCY)
    add_metric(Metric.INSERT_LATENCY)
    add_metric(Metric.INSERT_TPS)
    add_metric(Metric.DISK_USAGE)

    if return_old:
        old_benchmarks = get_old_benchmarks()
        new_benchmarks = []
        for benchmark in benchmarks:
            metric, new_value = benchmark
            old_value = old_benchmarks.get(metric.value)
            new_benchmarks.append((metric, old_value, new_value))
        benchmarks = new_benchmarks

    return benchmarks
