import os
import json
from github import Github
import urllib3
from core.utils.constants import Metric
from core.utils.process import get_experiment_result
import zipfile

REPO_NAME = 'lanterndata/lanterndb'
BASE_REF = os.environ.get('BASE_REF', 'main')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', None)

http = urllib3.PoolManager()


def get_old_benchmarks():
    if not GITHUB_TOKEN:
        print("GITHUB_TOKEN not set, skipping old benchmarks")
        return {}
    if not BASE_REF:
        print("BASE_REF not set, skipping old benchmarks")
        return {}

    print(f"Fetching old benchmarks from {BASE_REF}")
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    artifact = None
    workflows = repo.get_workflow_runs(branch=BASE_REF)

    for workflow in workflows:
        print(f"Checking artifacts for workflow run ID: {workflow.id}...")
        artifacts = workflow.get_artifacts()
        for artifact_ in artifacts:
            if artifact_.name == "benchmark-results":
                artifact = artifact_
                print(f"Found benchmark-results artifact")
                break
        if artifact:
            break

    if artifact:
        artifact_file_name = "/tmp/benchmark-results-artifact.zip"
        print(f"Downloading artifact to {artifact_file_name}...")

        url = artifact.archive_download_url
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "User-Agent": "Python",
        }
        r = http.request("GET", url, headers=headers)
        with open(artifact_file_name, "wb") as f:
            f.write(r.data)

        print(f"Extracting {artifact_file_name}...")
        with zipfile.ZipFile(artifact_file_name, 'r') as zip_ref:
            zip_ref.extractall("/tmp")

        print("Loading benchmark results from extracted JSON file...")
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

    add_metric(Metric.RECALL_AFTER_CREATE, use_K=True)
    add_metric(Metric.RECALL_AFTER_INSERT, use_K=True)
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
