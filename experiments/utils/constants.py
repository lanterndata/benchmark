from enum import Enum


"""
Extension constants
"""


class Extension(Enum):
    PGVECTOR = 'pgvector'
    LANTERN = 'lantern'
    NEON = 'neon'
    NONE = 'none'


EXTENSION_NAMES = {
    Extension.PGVECTOR: 'vector',
    Extension.LANTERN: 'lanterndb',
    Extension.NEON: 'embedding',
    Extension.NONE: 'lanterndb',
}

VALID_EXTENSIONS = [
    Extension.PGVECTOR,
    Extension.LANTERN,
    Extension.NEON,
]

DEFAULT_INDEX_PARAMS = {
    Extension.PGVECTOR: {'lists': 100, 'probes': 1},
    Extension.LANTERN: {'M': 2, 'ef_construction': 10, 'ef': 4},
    Extension.NEON: {'m': 2, 'efconstruction': 10, 'efsearch': 4},
}

VALID_INDEX_PARAMS = {
    index: list(default_params.keys()) for index, default_params in DEFAULT_INDEX_PARAMS.items()
}

"""
Metric constants
"""


class Metric(Enum):
    SELECT_LATENCY = 'select (latency ms)'

    SELECT_BULK_LATENCY = 'select bulk (latency ms)'

    SELECT_TPS = 'select (tps)'

    SELECT_BULK_TPS = 'select bulk (tps)'

    RECALL = 'recall'

    INSERT_LATENCY = 'insert (latency ms)'

    INSERT_BULK_LATENCY = 'insert bulk (latency ms)'

    INSERT_TPS = 'insert (tps)'

    INSERT_BULK_TPS = 'insert bulk (tps)'

    DISK_USAGE = 'disk usage (bytes)'

    CREATE_LATENCY = 'create (latency ms)'
    CREATE_LATENCY_STDDEV = 'create (latency stddev ms)'


VALID_METRICS = [metric.value for metric in Metric]

NO_INDEX_METRICS = [
    Metric.SELECT_LATENCY,
    Metric.SELECT_TPS,
    Metric.INSERT_LATENCY,
    Metric.INSERT_BULK_LATENCY,
]

"""
Experiment parameter constants
"""


class ExperimentParams(Enum):
    N = 'n'
    K = 'k'


EXPERIMENT_PARAMETERS = {
    Metric.SELECT_LATENCY: [ExperimentParams.N, ExperimentParams.K],
    Metric.SELECT_TPS: [ExperimentParams.N, ExperimentParams.K],
    Metric.RECALL: [ExperimentParams.N, ExperimentParams.K],
    Metric.INSERT_LATENCY: [],
    Metric.INSERT_BULK_LATENCY: [],
    Metric.DISK_USAGE: [ExperimentParams.N],
    Metric.CREATE_LATENCY: [ExperimentParams.N],
}

SUGGESTED_K_VALUES = [1, 3, 5, 10, 20, 40, 80]

"""
Dataset constants
"""


class Dataset(Enum):
    SIFT = 'sift'
    GIST = 'gist'


DATASET_DIMENSIONS = {
    Dataset.SIFT: 128,
    Dataset.GIST: 960,
}
VALID_DATASETS = [dataset.value for dataset in Dataset]

VALID_DATASET_SIZES = {
    Dataset.SIFT: ['10k', '100k', '200k', '400k', '600k', '800k', '1m'],
    Dataset.GIST: ['100k', '200k', '400k', '600k', '800k', '1m'],
}

VALID_DATASET_QUERY_SIZES = {
    Dataset.SIFT: ['10k', '1m', '1b'],
    Dataset.GIST: ['1m'],
}


def get_vector_dim(x):
    if isinstance(x, str):
        if 'sift' in x:
            dataset = Dataset.SIFT
        elif 'gist' in x:
            dataset = Dataset.GIST
    else:
        dataset = x
    return DATASET_DIMENSIONS[dataset]


"""
Table constants
"""

VALID_TABLE_TYPES = ['base', 'query', 'truth']
