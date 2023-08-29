import json
from .utils.database import DatabaseConnection
from .utils.constants import ExperimentParam, Metric, Extension, NO_INDEX_METRICS, EXPERIMENT_PARAMETERS, VALID_DATASET_SIZES, SUGGESTED_K_VALUES, Dataset
from .utils.numbers import convert_number_to_string
from . import select_experiment
from . import select_bulk_experiment
from . import create_experiment
from . import insert_experiment
from . import insert_bulk_experiment

# Parameter sets


def get_extension_parameter_sets(extension, metric_type):
    valid_parameter_sets = []
    for dataset in Dataset:
        if ExperimentParam.N in EXPERIMENT_PARAMETERS[metric_type]:
            valid_N = VALID_DATASET_SIZES[dataset]
            for N in valid_N:
                if ExperimentParam.K in EXPERIMENT_PARAMETERS[metric_type]:
                    for K in SUGGESTED_K_VALUES:
                        valid_parameter_sets.append((extension, dataset, N, K))
                else:
                    valid_parameter_sets.append((extension, dataset, N))
        else:
            valid_parameter_sets.append((extension, dataset))
    return valid_parameter_sets


def get_missing_extension_parameter_sets(extension, index_params, metric_type, valid_parameter_sets):
    if ExperimentParam.K in EXPERIMENT_PARAMETERS[metric_type]:
        columns = 'extension, dataset, n, k'
    if ExperimentParam.N in EXPERIMENT_PARAMETERS[metric_type]:
        columns = 'extension, dataset, n'
    else:
        columns = 'extension, dataset'
    sql = f"""
        SELECT
            {columns}
        FROM
            experiment_results
        WHERE
            metric_type = %s
            AND extension = %s
            AND index_params = %s
    """

    data = (metric_type.value, extension.value, json.dumps(index_params))
    with DatabaseConnection() as conn:
        found_parameter_sets = conn.select(sql, data=data)
    if ExperimentParam.N in EXPERIMENT_PARAMETERS[metric_type]:
        found_parameter_sets = {
            (Extension(e), Dataset(d), convert_number_to_string(n), *other)
            for (e, d, n, *other) in found_parameter_sets}
    else:
        found_parameter_sets = {
            (Extension(e), Dataset(d), *other)
            for (e, d, *other) in found_parameter_sets}

    missing_parameter_sets = [
        ps for ps in valid_parameter_sets if ps not in found_parameter_sets]
    return missing_parameter_sets


def group_parameter_sets_with_k(parameter_sets):
    grouped_dict = {}
    for parameter_set in parameter_sets:
        extension, dataset, N, K = parameter_set
        key = (extension, dataset, N)
        if key in grouped_dict:
            grouped_dict[key].append(K)
        else:
            grouped_dict[key] = [K]
    return [(*key, values) for key, values in grouped_dict.items()]

# Generate results


def get_generate_result(metric_type):
    if metric_type == Metric.SELECT_LATENCY or metric_type == Metric.SELECT_TPS:
        return select_experiment.generate_result
    if metric_type == Metric.SELECT_BULK_LATENCY or metric_type == Metric.SELECT_BULK_TPS:
        return select_bulk_experiment.generate_result
    if metric_type == Metric.DISK_USAGE:
        return disk_usage_experiment.generate_result
    if metric_type == Metric.CREATE_LATENCY:
        return create_experiment.generate_result
    if metric_type == Metric.INSERT_LATENCY or metric_type == Metric.INSERT_TPS:
        return insert_experiment.generate_result
    if metric_type == Metric.INSERT_BULK_LATENCY or metric_type == Metric.INSERT_BULK_TPS:
        return insert_bulk_experiment.generate_result


def generate_extension_results(extension, index_params, metric_type, missing_only=False):
    assert isinstance(metric_type, Metric)
    if extension is not None:
        assert isinstance(extension, Extension)
        if not metric_type in NO_INDEX_METRICS:
            assert extension != Extension.NONE

    parameter_sets = get_extension_parameter_sets(extension, metric_type)
    if missing_only:
        parameter_sets = get_missing_extension_parameter_sets(
            extension, index_params, metric_type, parameter_sets)
    if ExperimentParam.K in EXPERIMENT_PARAMETERS[metric_type]:
        parameter_sets = group_parameter_sets_with_k(parameter_sets)

    if len(parameter_sets) == 0:
        print('No parameter sets')
        return

    for parameter_set in parameter_sets:
        row = [getattr(element, 'value', element) if not isinstance(
            element, str) else element for element in parameter_set]
        print(' '.join(map(str, row)))
    print()

    generate_result = get_generate_result(metric_type)
    for parameter_set in parameter_sets:
        generate_result(*parameter_set, index_params)
