import sys
from utils import get_table_name, execute_sql

def delete_index(data, N, cur=None):
    table = get_table_name(data, N)
    sql = f"DELETE INDEX IF EXISTS {table}_index"
    execute_sql(sql, cur=cur)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise Exception('Usage: python delete_index.py data N')
    else:
        data = sys.argv[1]
        N = sys.argv[2]
        delete_index(data, N)
