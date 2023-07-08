import sys
import argparse
from .script_utils import get_table_name, execute_sql

def delete_index(dataset, N, conn=None, cur=None):
    table = get_table_name(dataset, N)
    sql = f"DROP INDEX IF EXISTS {table}_index"
    execute_sql(sql, conn=conn, cur=cur)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Delete index")
    parser.add_argument("--dataset", type=str, choices=['sift', 'gist'], required=True, help="Dataset name")
    parser.add_argument("--N", type=str, required=True, help="Dataset size")
    args = parser.parse_args()

    dataset = args.dataset
    N = args.N

    delete_index(dataset, N)
