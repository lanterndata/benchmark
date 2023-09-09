import ast
import os
import json
import logging
from github import Github
import urllib3
from core.utils.constants import Metric
from core.utils.process import get_experiment_result
import zipfile

REPO_NAME = 'lanterndata/lanterndb'
BASE_REF = os.environ.get('BASE_REF', 'main')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', None)

http = urllib3.PoolManager()


def can_literal_eval(s):
    try:
        ast.literal_eval(s)
        return True
    except (ValueError, SyntaxError):
        return False


def is_json_string(s):
    try:
        json.loads(s)
        return True
    except json.JSONDecodeError:
        return False


def get_old_benchmarks():
    try:
        if not GITHUB_TOKEN:
            logging.info("GITHUB_TOKEN not set, skipping old benchmarks")
            return {}
        if not BASE_REF:
            logging.info("BASE_REF not set, skipping old benchmarks")
            return {}

        logging.info(f"Fetching old benchmarks from {BASE_REF}")
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        artifact = None
        workflows = repo.get_workflow_runs(branch=BASE_REF)

        for workflow in workflows:
            logging.info(
                f"Checking artifacts for workflow run ID: {workflow.id}...")
            artifacts = workflow.get_artifacts()
            for artifact_ in artifacts:
                if artifact_.name == "benchmark-results":
                    artifact = artifact_
                    logging.info(f"Found benchmark-results artifact")
                    break
            if artifact:
                break

        if artifact:
            artifact_file_name = "/tmp/benchmark-results-artifact.zip"
            logging.info(f"Downloading artifact to {artifact_file_name}...")

            url = artifact.archive_download_url
            headers = {
                "Authorization": f"token {GITHUB_TOKEN}",
                "User-Agent": "Python",
            }
            r = http.request("GET", url, headers=headers)
            with open(artifact_file_name, "wb") as f:
                f.write(r.data)

            logging.info(f"Extracting {artifact_file_name}...")
            with zipfile.ZipFile(artifact_file_name, 'r') as zip_ref:
                zip_ref.extractall("/tmp")

            logging.info(
                "Loading benchmark results from extracted JSON file...")
            with open("/tmp/benchmarks-out.json", "r") as f:
                contents = f.read()
                if is_json_string(contents):
                    return json.load(f)
                elif can_literal_eval(contents):
                    return ast.literal_eval(contents)
                else:
                    logging.error("Could not parse benchmark results")
                    return {}

    except Exception as e:
        logging.error(f"Error fetching old benchmarks: {e}")

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
