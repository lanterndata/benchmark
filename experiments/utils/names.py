from .constants import VALID_DATASETS, VALID_TABLE_TYPES


def get_table_name(dataset, N, type='base'):
    if dataset not in VALID_DATASETS:
        raise Exception(
            f"Invalid dataset name = '{dataset}'. Valid dataset names are: {', '.join(VALID_DATASETS.keys())}")

    if N not in VALID_DATASETS[dataset]:
        raise Exception(
            f"Invalid N = '{N}'. Valid N values given dataset {dataset} are: {', '.join(VALID_DATASETS[dataset])}")

    if type not in VALID_TABLE_TYPES:
        raise Exception(
            f"Invalid table type = '{type}'. Valid table types are: {', '.join(VALID_TABLE_TYPES)}")

    table_name = f"{dataset}_{type}{N}"
    return table_name


def get_index_name(dataset, N):
    return get_table_name(dataset, N) + "_index"
