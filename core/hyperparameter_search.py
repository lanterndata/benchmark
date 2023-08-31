from .utils.constants import Extension
from .utils.numbers import convert_string_to_number
from .benchmark_select import generate_result
import math

HYPERPARAMETER_SEARCH_K = 5


def get_extension_hyperparameters(extension, N):
    hyperparameters = []
    if extension == Extension.PGVECTOR_IVFFLAT:
        sqrt_N = int(math.sqrt(convert_string_to_number(N)))
        lists_options = list(
            map(lambda p: int(p * sqrt_N), [0.6, 0.8, 1.0, 1.2, 1.4]))
        probes_options = [1, 2, 4, 8, 16, 32]
        hyperparameters = [{'lists': l, 'probes': p}
                           for l in lists_options for p in probes_options]
    if extension in [Extension.LANTERN, Extension.NEON, Extension.PGVECTOR_HNSW]:
        m_options = [4, 8, 16, 32, 64]
        ef_construction_options = [32, 64, 128]
        ef_options = [10, 20, 40]
        hyperparameters = [{'m': m, 'ef_construction': efc, 'ef': ef}
                           for m in m_options for efc in ef_construction_options for ef in ef_options
                           if efc > 2 * m]
    if extension == Extension.NONE:
        return [{}]
    return hyperparameters


def run_hyperparameter_search(extension, dataset, N, bulk=False):
    hyperparameters = get_extension_hyperparameters(extension, N)
    for hyperparameter in hyperparameters:
        generate_result(
            extension, dataset, N, [HYPERPARAMETER_SEARCH_K], index_params=hyperparameter, bulk=bulk)