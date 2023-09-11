import os
from .constants import Extension, Dataset
from .names import get_table_name, get_index_name
from .constants import coalesce_index_params, get_vector_dim, Extension
from .database import DatabaseConnection, get_database_url


def create_external_index(extension: Extension, dataset: Dataset, N: str, index_params={}):
    # Only Lantern is supported for now. Throw error if not Lantern
    if extension != Extension.LANTERN:
        raise NotImplementedError(
            f'Extension {extension.value} is not supported for external index creation')

    # Get data
    table = get_table_name(dataset, N)
    index = get_index_name(dataset, N)
    file = '/tmp/external-index.usearch'
    params = coalesce_index_params(extension, index_params)

    # Create external index and save to file
    database_url = get_database_url(extension)
    command = ' '.join([
        'ldb-create_index',
        '-u',
        f'"{database_url}"',
        '-t',
        f'"{table}"',
        '-c',
        '"v"',
        '-m',
        params['m'],
        '--ef',
        params['ef'],
        '--efc',
        params['ef_construction'],
        '-d',
        get_vector_dim(dataset),
        '--metric-kind',
        'cos',
        '--out',
        file
    ])
    os.system(command)

    # Create index from file
    sql = f"""
        CREATE INDEX {index}
        ON {table}
        USING hnsw (v)
        WITH (_experimental_index_path='{file}');
    """
    with DatabaseConnection(extension) as conn:
        conn.execute(sql)
    return
