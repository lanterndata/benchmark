from enum import Enum


"""
Extension constants
"""


class Extension(Enum):
    PGVECTOR_IVFFLAT = 'pgvector_ivfflat'
    PGVECTOR_HNSW = 'pgvector_hnsw'
    LANTERN = 'lantern'
    NEON = 'neon'
    NONE = 'none'


EXTENSION_VALUES = [extension.value for extension in Extension]

EXTENSION_NAMES = {
    Extension.PGVECTOR_IVFFLAT: 'vector',
    Extension.PGVECTOR_HNSW: 'vector',
    Extension.LANTERN: 'lanterndb',
    Extension.NEON: 'embedding',
    Extension.NONE: 'vector',
}

EXTENSIONS_USING_VECTOR = [Extension.PGVECTOR_IVFFLAT, Extension.PGVECTOR_HNSW, Extension.NONE]

DEFAULT_INDEX_PARAMS = {
    Extension.PGVECTOR_IVFFLAT: {'lists': 100, 'probes': 16},
    Extension.PGVECTOR_HNSW: {'m': 4, 'ef_construction': 128, 'ef': 10},
    Extension.LANTERN: {'m': 4, 'ef_construction': 128, 'ef': 10},
    Extension.NEON: {'m': 4, 'ef_construction': 128, 'ef': 10},
    Extension.NONE: {},
}

VALID_INDEX_PARAMS = {
    index: list(default_params.keys()) for index, default_params in DEFAULT_INDEX_PARAMS.items()
}

"""
Metric constants
"""


class Metric(Enum):

    # Select

    SELECT_LATENCY = 'select (latency ms)'
    SELECT_LATENCY_STDDEV = 'select (latency stddev ms)'

    SELECT_TPS = 'select (tps)'

    RECALL = 'recall'

    BUFFER_SHARED_HIT_COUNT = 'buffer shared hits'
    BUFFER_SHARED_HIT_COUNT_STDDEV = 'buffer shared hits (stddev)'

    BUFFER_READ_COUNT = 'buffer disk reads'
    BUFFER_READ_COUNT_STDDEV = 'buffer disk reads (stddev)'

    # Select bulk

    SELECT_BULK_LATENCY = 'select bulk (latency ms)'
    SELECT_BULK_LATENCY_STDDEV = 'select bulk (latency stddev ms)'

    SELECT_BULK_TPS = 'select bulk (tps)'

    BUFFER_BULK_SHARED_HIT_COUNT = 'bulk buffer shared hits'
    BUFFER_BULK_SHARED_HIT_COUNT_STDDEV = 'bulk buffer shared hits (stddev)'

    BUFFER_BULK_READ_COUNT = 'bulk buffer disk reads'
    BUFFER_BULK_READ_COUNT_STDDEV = 'bulk buffer disk reads (stddev)'

    # Insert

    INSERT_LATENCY = 'insert (latency ms)'
    INSERT_LATENCY_STDDEV = 'insert (latency stddev ms)'

    INSERT_TPS = 'insert (tps)'

    # Insert bulk

    INSERT_BULK_LATENCY = 'insert bulk (latency ms)'
    INSERT_BULK_LATENCY_STDDEV = 'insert bulk (latency stddev ms)'

    INSERT_BULK_TPS = 'insert bulk (tps)'

    # Create

    DISK_USAGE = 'disk usage (bytes)'
    DISK_USAGE_STDDEV = 'disk usage (stddev bytes)'

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


class ExperimentParam(Enum):
    N = 'n'
    K = 'k'


EXPERIMENT_PARAMETERS = {
    Metric.SELECT_LATENCY: [ExperimentParam.N, ExperimentParam.K],
    Metric.SELECT_TPS: [ExperimentParam.N, ExperimentParam.K],
    Metric.RECALL: [ExperimentParam.N, ExperimentParam.K],
    Metric.INSERT_LATENCY: [],
    Metric.INSERT_BULK_LATENCY: [],
    Metric.DISK_USAGE: [ExperimentParam.N],
    Metric.CREATE_LATENCY: [ExperimentParam.N],
    Metric.BUFFER_READ_COUNT: [ExperimentParam.N, ExperimentParam.K],
    Metric.BUFFER_SHARED_HIT_COUNT: [ExperimentParam.N, ExperimentParam.K],
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
    Dataset.SIFT: ['10k', '100k', '200k', '400k', '600k', '800k', '1m', '2m', '5m', '10m', '20m', '50m', '100m', '200m', '500m', '1b'],
    Dataset.GIST: ['100k', '200k', '400k', '600k', '800k', '1m'],
}

VALID_DATASET_QUERY_SIZES = {
    Dataset.SIFT: ['10k', '1m', '1b'],
    Dataset.GIST: ['1m'],
}

SUGGESTED_DATASET_SIZES = {
    Dataset.SIFT: ['10k', '100k', '200k', '400k', '600k', '800k', '1m']
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
