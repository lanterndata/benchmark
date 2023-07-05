import sys
from utils import get_table_name, execute_sql

def create_index(data, N, lists=100, cur=None):
    table = get_table_name(data, N)
    sql = f"CREATE INDEX IF NOT EXISTS {table}_index ON {table} USING (v vector_l2_ops) WITH (lists = {lists})"
    execute_sql(sql, cur=cur)

if __name__ == '__main__':
    if len(sys.argv) != 4 and len(sys.argv) != 3:
        raise Exception('Usage: python create_index.py data N (lists)')
    else:
        data = sys.argv[1]
        N = sys.argv[2]
        lists = int(sys.argv[3]) if len(sys.argv) == 4 else None
        if lists is None:
            create_index(data, N)
        else:
            create_index(data, N, lists=lists)