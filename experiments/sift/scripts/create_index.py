import argparse
from .script_utils import get_table_name, execute_sql

def create_pgvector_index(dataset, N, lists=5, conn=None, cur=None):
    table = get_table_name(dataset, N)
    index = f"{table}_index"
    sql = f"""
      CREATE INDEX IF NOT EXISTS {index} ON {table} USING
      ivfflat (v vector_l2_ops) WITH (lists = {lists})
    """
    execute_sql(sql, conn=conn, cur=cur)
    return index

def create_lantern_index(dataset, N, conn=None, cur=None):
    table = get_table_name(dataset, N)
    index = f"{table}_index"
    sql = f"""
      CREATE INDEX IF NOT EXISTS {index} ON {table} USING
      embedding (v vector_l2_ops)
    """
    execute_sql(sql, conn=conn, cur=cur)
    return index

def create_index(extension, *args, **kwargs):
    if extension == 'lantern':
        create_lantern_index(*args, **kwargs)
    else:
        create_pgvector_index(*args, **kwargs)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create index")
    parser.add_argument('--extension', type=str, choices=['lantern', 'pgvector'], help='Extension type')
    parser.add_argument("--dataset", type=str, choices=['sift', 'gist'], required=True, help="Dataset name")
    parser.add_argument("--N", type=str, required=True, help="Dataset size")
    extension_group = parser.add_argument_group('pgvector arguments')
    extension_group.add_argument('--lists', type=int, help='Number of lists')
    args = parser.parse_args()

    extension = args.extension
    dataset = args.dataset
    N = args.N
    lists = args.lists

    if extension == 'lantern':
        create_lantern_index(dataset, N)
    else:
        lists = args.lists
        create_pgvector_index(dataset, N, lists=lists)
