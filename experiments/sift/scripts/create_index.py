import sys
from .script_utils import get_table_name, execute_sql

def create_index(dataset, N, lists=10, conn=None, cur=None):
    table = get_table_name(dataset, N)
    index = f"{table}_index"
    sql = f"CREATE INDEX IF NOT EXISTS {index} ON {table} USING ivfflat (v vector_l2_ops) WITH (lists = {lists})"
    execute_sql(sql, conn=conn, cur=cur)
    return index

if __name__ == '__main__':
    if len(sys.argv) != 4 and len(sys.argv) != 3:
        raise Exception('Usage: python create_index.py sift 10k (lists)')

    dataset = sys.argv[1]
    N = sys.argv[2]
    lists = int(sys.argv[3]) if len(sys.argv) == 4 else None
    if lists is None:
        create_index(dataset, N)
    else:
        create_index(dataset, N, lists=lists)