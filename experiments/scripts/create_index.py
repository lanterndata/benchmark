from .script_utils import parse_args, get_table_name, get_index_name, execute_sql, DEFAULT_INDEX_PARAMS, VALID_INDEX_PARAMS, VALID_DATASETS

def get_create_pg_vector_index_query(dataset, N, index_params):
    table = get_table_name(dataset, N)
    index = get_index_name(dataset, N)
    params = { **DEFAULT_INDEX_PARAMS['pgvector'], **index_params }
    sql = f"""
        CREATE INDEX IF NOT EXISTS {index} ON {table} USING
        ivfflat (v) WITH (
            lists = {params['lists']}
        )
    """
    return sql

def create_pgvector_index(dataset, N, index_params={}, conn=None, cur=None):
    sql = get_create_pg_vector_index_query(dataset, N, index_params)
    execute_sql(sql, conn=conn, cur=cur)

def get_create_lantern_index_query(dataset, N, index_params):
    table = get_table_name(dataset, N)
    index = get_index_name(dataset, N)
    params = { **DEFAULT_INDEX_PARAMS['lantern'], **index_params }
    sql = f"""
        CREATE INDEX IF NOT EXISTS {index} ON {table} USING
        hnsw (v) WITH (
            M={params['M']},
            ef_construction={params['ef_construction']},
            ef={params['ef']}
        )
    """
    return sql

def create_lantern_index(dataset, N, index_params={}, conn=None, cur=None):
    sql = get_create_lantern_index_query(dataset, N, index_params)
    execute_sql(sql, conn=conn, cur=cur)

def get_create_index_query(extension, *args, **kwargs):
    if extension == 'lantern':
        return get_create_lantern_index_query(*args, **kwargs)
    elif extension == 'pgvector':
        return get_create_pg_vector_index_query(*args, **kwargs)

def create_index(extension, *args, **kwargs):
    if extension == 'lantern':
        return create_lantern_index(*args, **kwargs)
    elif extension == 'pgvector':
        return create_pgvector_index(*args, **kwargs)

if __name__ == '__main__':
    extension, index_params, dataset, N_values, _ = parse_args("create index", args=['extension', 'N'])
    for N in N_values:
        if extension == 'lantern':
            create_lantern_index(dataset, N, index_params)
        elif extension == 'pgvector':
            create_pgvector_index(dataset, N, index_params)
