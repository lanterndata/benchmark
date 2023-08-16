from .cli import parse_args
from .names import get_table_name, get_index_name
from .constants import DEFAULT_INDEX_PARAMS, get_vector_dim
from .database import DatabaseConnection


def get_index_params(extension, index_params):
    return {**DEFAULT_INDEX_PARAMS[extension], **index_params}


def get_create_pgvector_index_query(table, index, index_params):
    params = get_index_params('pgvector', index_params)
    sql = f"""
        SET maintenance_work_mem = '2GB';
        CREATE INDEX {index} ON {table} USING
        ivfflat (v vector_l2_ops) WITH (
            lists = {params['lists']}
        );
        SET LOCAL ivfflat.probes = {params['probes']};
        SET enable_seqscan = off;
    """
    return sql


def get_create_lantern_index_query(table, index, index_params):
    params = get_index_params('lantern', index_params)
    sql = f"""
        SET maintenance_work_mem = '2GB';
        CREATE INDEX {index} ON {table} USING
        hnsw (v) WITH (
            M={params['M']},
            ef_construction={params['ef_construction']},
            ef={params['ef']}
        );
        SET enable_seqscan = off;
    """
    return sql


def get_create_neon_index_query(table, index, index_params):
    params = get_index_params('neon', index_params)
    vector_dim = get_vector_dim(table)
    sql = f"""
        SET maintenance_work_mem = '2GB';
        CREATE INDEX {index} ON {table} USING
        hnsw (v) WITH (
            dims={vector_dim},
            m={params['m']},
            efconstruction={params['efconstruction']},
            efsearch={params['efsearch']}
        );
        SET enable_seqscan = off;
    """
    return sql


def create_custom_index_query(extension, table, index, index_params):
    if extension == 'lantern':
        return get_create_lantern_index_query(table, index, index_params)
    elif extension == 'pgvector':
        return get_create_pgvector_index_query(table, index, index_params)
    elif extension == 'neon':
        return get_create_neon_index_query(table, index, index_params)


def get_create_index_query(extension, dataset, N, index_params):
    table = get_table_name(dataset, N)
    index = get_index_name(dataset, N)
    return create_custom_index_query(extension, table, index, index_params)


def create_custom_index(extension, table, index, index_params={}):
    sql = create_custom_index_query(extension, table, index, index_params)
    if sql is not None:
        with DatabaseConnection(extension) as conn:
            conn.execute(sql)


def create_index(extension, dataset, N, index_params={}):
    sql = get_create_index_query(extension, dataset, N, index_params)
    if sql is not None:
        with DatabaseConnection(extension) as conn:
            conn.execute(sql)


if __name__ == '__main__':
    extension, index_params, dataset, N_values, _ = parse_args(
        "create index", args=['extension', 'N'])
    for N in N_values:
        create_index(extension, dataset, N, index_params)
