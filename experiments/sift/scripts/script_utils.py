import os
import psycopg2

VALID_DATA = {
    'sift': ['10k', '100k', '200k', '400k', '600k', '800k', '1m'],
    'gist': ['10k', '100k', '200k', '400k', '600k', '800k', '1m'],
}

def get_table_name(data, N):
    if data not in VALID_DATA:
        raise Exception(f"Invalid data name. Valid data names are: {', '.join(VALID_DATA.keys())}")

    if N not in VALID_DATA[data]:
        raise Exception(f"Invalid N. Valid N values given data {data} are: {', '.join(VALID_DATA[data])}")
    
    return f"{data}_base{N}"

def execute_sql(sql, cur=None):
    conn = None

    if cur is None:
        database_url = os.environ.get('DATABASE_URL')
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()

    cur.execute(sql)

    if conn is not None:
        cur.close()
        conn.close()