import argparse
from script_utils import get_index_name, execute_sql, parse_args

def get_drop_index_query(dataset, N):
    index_name = get_index_name(dataset, N)
    sql = f"DROP INDEX IF EXISTS {index_name}"
    return sql

def delete_index(dataset, N, conn=None, cur=None):
    if dataset == 'none':
      return
    sql = get_drop_index_query(dataset, N)
    execute_sql(sql, conn=conn, cur=cur)

if __name__ == '__main__':
    _, _, dataset, N_values, _ = parse_args("delete index", args=['N'])
    for N in N_values:
        delete_index(dataset, N)
