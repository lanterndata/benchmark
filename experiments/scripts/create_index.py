import argparse
from .script_utils import get_table_name, get_index_name, execute_sql

def get_create_pg_vector_index_query(dataset, N, lists=100):
    table = get_table_name(dataset, N)
    index = get_index_name(dataset, N)
    sql = f"""
      CREATE INDEX IF NOT EXISTS {index} ON {table} USING
      ivfflat (v vector_l2_ops) WITH (lists = {lists})
    """
    return sql

def create_pgvector_index(dataset, N, conn=None, cur=None):
    sql = get_create_pg_vector_index_query(dataset, N)
    execute_sql(sql, conn=conn, cur=cur)

def get_create_lantern_index_query(dataset, N):
    table = get_table_name(dataset, N)
    index = get_index_name(dataset, N)
    sql = f"""
      CREATE INDEX IF NOT EXISTS {index} ON {table} USING
      embedding (v vector_l2_ops)
    """
    return sql

def create_lantern_index(dataset, N, conn=None, cur=None):
    sql = get_create_lantern_index_query(dataset, N)
    execute_sql(sql, conn=conn, cur=cur)

def get_create_index_query(extension, *args):
    if extension == 'lantern':
        return get_create_lantern_index_query(*args)
    else:
        return get_create_pg_vector_index_query(*args)

def create_index(extension, *args, **kwargs):
    if extension == 'lantern':
        return create_lantern_index(*args, **kwargs)
    else:
        return create_pgvector_index(*args, **kwargs)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create index")
    parser.add_argument('--extension', type=str, choices=['lantern', 'pgvector'], help='Extension type')
    parser.add_argument("--dataset", type=str, choices=['sift', 'gist'], required=True, help="Dataset name")
    parser.add_argument("--N", type=str, required=True, help="Dataset size")
    args = parser.parse_args()

    extension = args.extension
    dataset = args.dataset
    N = args.N
    lists = args.lists

    if extension == 'lantern':
        create_lantern_index(dataset, N)
    else:
        create_pgvector_index(dataset, N)
