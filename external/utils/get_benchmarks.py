from core.utils.constants import Metric
from core.utils.process import get_experiment_result

def get_benchmarks(extension, index_params, dataset, N, K, return_old=False):
    metrics = []

    new_recall = get_experiment_result(Metric.RECALL, extension, index_params, dataset, N, K)
    if return_old:
        old_recall = 0.0  # TODO
        metrics.append((Metric.RECALL, old_recall, new_recall))
    else:
        metrics.append((Metric.RECALL, new_recall))
    
    return metrics
