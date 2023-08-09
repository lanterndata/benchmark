from .script_utils import parse_args, get_table_name, get_index_name, execute_sql, DEFAULT_INDEX_PARAMS, VALID_INDEX_PARAMS, VALID_DATASETS

def get_create_pgvector_index_query(table, index, index_params):
    params = { **DEFAULT_INDEX_PARAMS['pgvector'], **index_params }
    sql = f"""
        SET maintenance_work_mem = '1GB';
        CREATE INDEX IF NOT EXISTS {index} ON {table} USING
        ivfflat (v vector_l2_ops) WITH (
            lists = {params['lists']}
        );
        SET LOCAL ivfflat.probes = {params['probes']};
    """
    return sql

def get_create_lantern_index_query(table, index, index_params):
    params = { **DEFAULT_INDEX_PARAMS['lantern'], **index_params }
    sql = f"""
        SET maintenance_work_mem = '1GB';
        CREATE INDEX IF NOT EXISTS {index} ON {table} USING
        hnsw (v) WITH (
            M={params['M']},
            ef_construction={params['ef_construction']},
            ef={params['ef']}
        )
    """
    return sql

def create_custom_index_query(extension, table, index, index_params, conn=None, cur=None):
    if extension == 'lantern':
        return get_create_lantern_index_query(table, index, index_params)
    elif extension == 'pgvector':
        return get_create_pgvector_index_query(table, index, index_params)

def get_create_index_query(extension, dataset, N, index_params):
    table = get_table_name(dataset, N)
    index = get_index_name(dataset, N)
    return create_custom_index_query(extension, table, index, index_params)

def create_custom_index(*args, **kwargs):
    sql = create_custom_index_query(*args, **kwargs)
    if sql is not None:
        execute_sql(sql, conn=None, cur=None)

def create_index(extension, dataset, N, index_params={}, conn=None, cur=None):
    sql = get_create_index_query(extension, dataset, N, index_params)
    if sql is not None:
        execute_sql(sql, conn=None, cur=None)

if __name__ == '__main__':
    extension, index_params, dataset, N_values, _ = parse_args("create index", args=['extension', 'N'])
    for N in N_values:
        create_index(extension, dataset, N, index_params)
