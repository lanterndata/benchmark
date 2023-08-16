from .constants import Dataset, VALID_TABLE_TYPES, VALID_DATASET_SIZES, VALID_DATASETS


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

    table_name = f"{dataset.value}_{type}{N}"
    return table_name


def get_index_name(dataset, N):
    return get_table_name(dataset, N) + "_index"
