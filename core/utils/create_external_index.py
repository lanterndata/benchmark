import os
from .constants import Extension, Dataset
from .names import get_table_name, get_index_name
from .constants import coalesce_index_params, get_vector_dim, Extension
from .database import get_database_url, run_command


DIR = '/tmp/external_indexes'

def create_external_index(extension: Extension, dataset: Dataset, N: str, index_params={}):
    # Only Lantern is supported for now. Throw error if not Lantern
    if extension != Extension.LANTERN:
        raise NotImplementedError(
            f'Extension {extension.value} is not supported for external index creation')

    # Throw error if this should not be an external index
    if 'external' not in index_params or not index_params['external']:
        raise ValueError(
            f'Index params {index_params} do not specify an external index')

    # Create directory for data
    if not os.path.exists(DIR):
        os.makedirs(DIR)

    # Get data
    table = get_table_name(dataset, N)
    index = get_index_name(dataset, N)
    params = coalesce_index_params(extension, index_params)
    index_file = f"{DIR}/{index}.usearch"

    # Create external index
    database_url = get_database_url(extension)
    command = ' '.join([
        'sshpass -p root ssh -o StrictHostKeyChecking=no -p 22 root@lantern',
        'lantern-cli create-index',
        f"-u '{database_url}'",
        f"-t \"{table}\"",
        '-c "v"',
        f"-m {params['m']}",
        f"--ef {params['ef']}",
        f"--efc {params['ef_construction']}",
        f"-d {get_vector_dim(dataset)}",
        '--metric-kind l2sq',
        f"--out {index_file}",
        f"--import",
    ])
    _, err = run_command(command)
    if err:
        print(err)

