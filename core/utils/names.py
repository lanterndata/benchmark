from .constants import Dataset, VALID_TABLE_TYPES, VALID_DATASET_SIZES, VALID_DATASETS, VALID_DATASET_QUERY_SIZES
from .numbers import convert_string_to_number, convert_number_to_string


def get_table_name(dataset, N, type='base'):
    if dataset not in Dataset:
        raise Exception(
            f"Invalid dataset name = '{dataset.value}'. Valid dataset names are: {', '.join(VALID_DATASETS)}")

    if N not in VALID_DATASET_SIZES[dataset]:
        raise Exception(
            f"Invalid N = '{N}'. Valid N values given dataset {dataset.value} are: {', '.join(VALID_DATASET_SIZES[dataset])}")

    if type not in VALID_TABLE_TYPES:
        raise Exception(
            f"Invalid table type = '{type}'. Valid table types are: {', '.join(VALID_TABLE_TYPES)}")

    if type == 'query':
        dataset_query_sizes = map(
            convert_string_to_number, VALID_DATASET_QUERY_SIZES[dataset])
        dataset_size = convert_string_to_number(N)
        for dataset_query_size in dataset_query_sizes:
            if dataset_query_size >= dataset_size:
                N = convert_number_to_string(dataset_query_size)
                break
    table_name = f"{dataset.value}_{type}{N}"
    return table_name

def get_cloud_index_name(dataset, N, type='base'):
    table_name = get_table_name(dataset, N, type)
    return table_name.replace('_', '-')

def get_index_name(dataset, N):
    return get_table_name(dataset, N) + "_index"
