from .names import get_index_name
from .database import DatabaseConnection


def get_drop_index_query(dataset, N):
    index_name = get_index_name(dataset, N)
    sql = f"DROP INDEX IF EXISTS {index_name};"
    return sql


def delete_index(extension, dataset, N):
    commands = ['SET enable_seqscan = on;']
    if extension != 'none':
        commands.append(get_drop_index_query(dataset, N))
    if extension == 'lantern':
        commands.append('DROP EXTENSION IF EXISTS lantern;')
    if extension == 'neon':
        commands.append('DROP EXTENSION IF EXISTS embedding;')
    sql = '\n'.join(commands)
    with DatabaseConnection(extension) as conn:
        conn.execute(sql)
