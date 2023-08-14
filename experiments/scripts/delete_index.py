from .script_utils import get_index_name, execute_sql, parse_args


def get_drop_index_query(extension, dataset, N):
    index_name = get_index_name(extension, dataset, N)
    sql = f"DROP INDEX IF EXISTS {index_name};"
    return sql


def delete_index(extension, dataset, N, conn=None, cur=None):
    commands = ['SET enable_seqscan = on;']
    if extension != 'none':
        commands.append(get_drop_index_query(extension, dataset, N))
    if extension == 'lantern':
        commands.append('DROP EXTENSION IF EXISTS lantern;')
    if extension == 'neon':
        commands.append('DROP EXTENSION IF EXISTS embedding;')
    sql = '\n'.join(commands)
    execute_sql(sql, conn=conn, cur=cur)


if __name__ == '__main__':
    extension, _, dataset, N_values, _ = parse_args(
        "delete index", args=['extension', 'N'])
    for N in N_values:
        delete_index(extension, dataset, N)
