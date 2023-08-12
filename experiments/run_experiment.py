from scripts.script_utils import execute_sql, VALID_METRICS, METRICS_WITH_K, METRICS_WITHOUT_N, VALID_EXTENSIONS, VALID_EXTENSIONS_AND_NONE, VALID_DATASETS, VALID_QUERY_DATASETS, SUGGESTED_K_VALUES
from scripts.number_utils import convert_number_to_string
import recall_experiment
import select_experiment
import disk_usage_experiment
import create_experiment
import insert_experiment
import insert_bulk_experiment

# Parameter sets


def get_extension_parameter_sets(extension, metric_type):
    valid_parameter_sets = []
    for dataset in VALID_DATASETS.keys():
        if metric_type in METRICS_WITHOUT_N:
            valid_parameter_sets.append((extension, dataset))
        else:
            valid_N = VALID_QUERY_DATASETS[dataset] if metric_type == 'recall' else VALID_DATASETS[dataset]
            for N in valid_N:
                if metric_type in METRICS_WITH_K:
                    for K in SUGGESTED_K_VALUES:
                        valid_parameter_sets.append((extension, dataset, N, K))
                else:
                    valid_parameter_sets.append((extension, dataset, N))
    return valid_parameter_sets


def get_missing_extension_parameter_sets(extension, extension_params, metric_type, valid_parameter_sets):
    if metric_type in METRICS_WITH_K:
        columns = 'database, dataset, n, k'
    elif metric_type in METRICS_WITHOUT_N:
        columns = 'database, dataset'
    else:
        columns = 'database, dataset, n'
    sql = f"""
        SELECT
            {columns}
        FROM
            experiment_results
        WHERE
            metric_type = %s
            AND database = %s
            AND database_params = %s
    """

    data = (metric_type, extension, extension_params)
    found_parameter_sets = execute_sql(sql, data=data, select=True)
    if metric_type in METRICS_WITHOUT_N:
        found_parameter_sets = {(database, dataset, convert_number_to_string(
            n), *rest) for (database, dataset, n, *rest) in found_parameter_sets}

    missing_parameter_sets = [
        parameter_set for parameter_set in valid_parameter_sets if parameter_set not in found_parameter_sets]
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
    if metric_type == 'select (tps)':
        return select_experiment.generate_result
    if metric_type == 'select (latency ms)':
        return select_experiment.generate_result
    if metric_type == 'recall':
        return recall_experiment.generate_result
    if metric_type == 'disk usage (bytes)':
        return disk_usage_experiment.generate_result
    if metric_type == 'create (latency ms)':
        return create_experiment.generate_result
    if metric_type == 'insert (latency s)':
        return insert_experiment.generate_result
    if metric_type == 'insert bulk (latency s)':
        return insert_bulk_experiment.generate_result


def generate_extension_results(extension, extension_params, metric_type, missing_only=False):
    assert metric_type in VALID_METRICS
    if extension is not None:
        if 'select' in metric_type or 'recall' in metric_type or 'insert' in metric_type:
            assert extension in VALID_EXTENSIONS_AND_NONE
        else:
            assert extension in VALID_EXTENSIONS

    parameter_sets = get_extension_parameter_sets(extension, metric_type)
    if missing_only:
        parameter_sets = get_missing_extension_parameter_sets(
            extension, extension_params, metric_type, parameter_sets)
    if metric_type in METRICS_WITH_K:
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
