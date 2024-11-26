from .names import get_table_name, get_index_name
from .constants import coalesce_index_params, get_vector_dim, Extension
from .database import DatabaseConnection
from .create_external_index import create_external_index


def get_create_pgvector_ivfflat_index_query(table, index, index_params):
    params = coalesce_index_params(Extension.PGVECTOR_IVFFLAT, index_params)
    sql = f"""
        SET maintenance_work_mem = '2GB';
        CREATE INDEX {index} ON {table} USING
        ivfflat (v vector_cosine_ops) WITH (
            lists = {params['lists']}
        );
        SET LOCAL ivfflat.probes = {params['probes']};
        SET enable_seqscan = off;
    """
    return sql


def get_create_pgvector_hnsw_index_query(table, index, index_params):
    params = coalesce_index_params(Extension.PGVECTOR_HNSW, index_params)
    sql = f"""
        SET maintenance_work_mem = '2GB';
        CREATE INDEX {index} ON {table} USING
        hnsw (v vector_cosine_ops) WITH (
            m={params['m']},
            ef_construction={params['ef_construction']},
            external={params['external']}
        );
        SET LOCAL hnsw.ef_search = {params['ef']};
        SET enable_seqscan = off;
    """
    return sql


def get_create_lantern_index_query(table, index, index_params):
    params = coalesce_index_params(Extension.LANTERN, index_params)
    vector_dim = get_vector_dim(table)
    sql = f"""
        SET maintenance_work_mem = '2GB';
        SET lantern.external_index_host='127.0.0.1';
        SET lantern.external_index_port=8998;
        SET lantern.external_index_secure=false;
        CREATE INDEX {index} ON {table} USING
        lantern_hnsw (v dist_cos_ops) WITH (
            dim={vector_dim},
            M={params['m']},
            ef_construction={params['ef_construction']},
            ef={params['ef']},
            external={params['external']}
        );
        SET enable_seqscan = off;
    """
    return sql


def get_create_neon_index_query(table, index, index_params):
    params = coalesce_index_params(Extension.NEON, index_params)
    vector_dim = get_vector_dim(table)
    sql = f"""
        SET maintenance_work_mem = '2GB';
        CREATE INDEX {index} ON {table} USING
        hnsw (v) WITH (
            dims={vector_dim},
            m={params['m']},
            efconstruction={params['ef_construction']},
            efsearch={params['ef']}
        );
        SET enable_seqscan = off;
    """
    return sql


def create_custom_index_query(extension, table, index, index_params):
    if extension == Extension.LANTERN:
        return get_create_lantern_index_query(table, index, index_params)
    elif extension == Extension.PGVECTOR_IVFFLAT:
        return get_create_pgvector_ivfflat_index_query(table, index, index_params)
    elif extension == Extension.PGVECTOR_HNSW:
        return get_create_pgvector_hnsw_index_query(table, index, index_params)
    elif extension == Extension.NEON:
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
