import sys
from .script_utils import get_table_name, execute_sql

def delete_index(dataset, N, conn=None, cur=None):
    table = get_table_name(dataset, N)
    sql = f"DROP INDEX IF EXISTS {table}_index"
    execute_sql(sql, conn=conn, cur=cur)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise Exception('Usage: python delete_index.py sift 10k')

    dataset = sys.argv[1]
    N = sys.argv[2]
    delete_index(dataset, N)
