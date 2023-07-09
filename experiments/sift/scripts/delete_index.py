import argparse
from .script_utils import get_index_name, execute_sql

def get_drop_index_query(dataset, N):
    index_name = get_index_name(dataset, N)
    sql = f"DROP INDEX IF EXISTS {index_name}"
    return sql

def delete_index(dataset, N, conn=None, cur=None):
    sql = get_drop_index_query(dataset, N)
    execute_sql(sql, conn=conn, cur=cur)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Delete index")
    parser.add_argument("--dataset", type=str, choices=['sift', 'gist'], required=True, help="Dataset name")
    parser.add_argument("--N", type=str, required=True, help="Dataset size")
    args = parser.parse_args()

    dataset = args.dataset
    N = args.N

    delete_index(dataset, N)
