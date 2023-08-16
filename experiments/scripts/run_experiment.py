from utils.database import DatabaseConnection
from utils.constants import ExperimentParams, Metric, NO_INDEX_METRICS, EXPERIMENT_PARAMETERS, VALID_METRICS, VALID_EXTENSIONS, VALID_EXTENSIONS_AND_NONE, VALID_DATASET_SIZES, VALID_QUERY_DATASET_SIZES, SUGGESTED_K_VALUES, Dataset
from utils.numbers import convert_number_to_string
import select_experiment
import select_bulk_experiment
import disk_usage_experiment
import create_experiment
import insert_experiment
import insert_bulk_experiment

# Parameter sets


def get_extension_parameter_sets(extension, metric_type):
    valid_parameter_sets = []
    for dataset in Dataset:
        if ExperimentParams.N in EXPERIMENT_PARAMETERS[metric_type]:
            valid_parameter_sets.append((extension, dataset))
        else:
            if metric_type == Metric.RECALL:
                valid_N = VALID_QUERY_DATASET_SIZES[dataset]
            else:
                valid_N = VALID_DATASET_SIZES[dataset]
            for N in valid_N:
                if ExperimentParams.K in EXPERIMENT_PARAMETERS[metric_type]:
                    for K in SUGGESTED_K_VALUES:
                        valid_parameter_sets.append((extension, dataset, N, K))
                else:
                    valid_parameter_sets.append((extension, dataset, N))
    return valid_parameter_sets


def get_missing_extension_parameter_sets(extension, extension_params, metric_type, valid_parameter_sets):
    if ExperimentParams.K in EXPERIMENT_PARAMETERS[metric_type]:
        columns = 'extension, dataset, n, k'
    if ExperimentParams.N in EXPERIMENT_PARAMETERS[metric_type]:
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

    data = (metric_type, extension, extension_params)
    with DatabaseConnection(extension) as conn:
        found_parameter_sets = conn.select(sql, data=data)
    if len(EXPERIMENT_PARAMETERS[metric_type]) == 0:
        found_parameter_sets = {(database, dataset, convert_number_to_string(
            n), *rest) for (database, dataset, n, *rest) in found_parameter_sets}

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


def generate_extension_results(extension, extension_params, metric_type, missing_only=False):
    assert metric_type in VALID_METRICS
    if extension is not None:
        if extension in NO_INDEX_METRICS:
            assert extension in VALID_EXTENSIONS_AND_NONE
        else:
            assert extension in VALID_EXTENSIONS

    parameter_sets = get_extension_parameter_sets(extension, metric_type)
    if missing_only:
        parameter_sets = get_missing_extension_parameter_sets(
            extension, extension_params, metric_type, parameter_sets)
    if ExperimentParams.K in EXPERIMENT_PARAMETERS[metric_type]:
        parameter_sets = group_parameter_sets_with_k(parameter_sets)

    if len(parameter_sets) == 0:
        print('No parameter sets')
        return

    for parameter_set in parameter_sets:
        print(parameter_set)
    print()

    generate_result = get_generate_result(metric_type)
    for parameter_set in parameter_sets:
        generate_result(*parameter_set, extension_params)
