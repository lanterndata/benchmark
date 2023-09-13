import os
import psycopg2
import logging
import subprocess
import os
import re
from tempfile import NamedTemporaryFile
from .constants import Extension


class DatabaseConnection:
    def __init__(self, extension=None, autocommit=False):
        self.extension = extension
        self.autocommit = autocommit

    def __enter__(self):
        self.conn = psycopg2.connect(get_database_url(self.extension))
        self.conn.autocommit = self.autocommit
        self.cur = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.cur.close()
        self.conn.close()

    def copy_expert(self, sql, file):
        """
        Use psycopg2's copy_expert method to copy data between a file and the database.

        Parameters:
        - sql (str): The SQL command to run.
        - file: A file-like object to copy to/from. Can be an actual file or a StringIO object.
        - data (tuple, optional): Parameters to use with the SQL command.
        """
        try:
            self.cur.copy_expert(sql, file)
            self.conn.commit()
        except Exception as e:
            logging.error("Error using copy_expert: %s", e)
            logging.error("SQL query: %s", sql)
            raise

    def select_one(self, sql, data=None):
        """
        Execute a SELECT query and return the first result.
        """
        self._execute(sql, data)
        data = self.cur.fetchone()
        return data

    def select(self, sql, data=None):
        """
        Execute a SELECT query and return all results.
        """
        self._execute(sql, data)
        data = self.cur.fetchall()
        return data

    def execute(self, sql, data=None):
        """
        Execute a query (INSERT, UPDATE, DELETE) and commit changes.
        """
        self._execute(sql, data)
        self.conn.commit()

    def _execute(self, sql, data=None):
        """
        Execute a SQL query with optional parameters.
        """
        try:
            if data is None:
                self.cur.execute(sql)
            else:
                self.cur.execute(sql, data)
        except Exception as e:
            logging.error("Error executing SQL: %s", e)
            logging.error("SQL query: %s", sql)
            raise


def run_pgbench(extension, query, clients=8, threads=8, transactions=15):
    with NamedTemporaryFile(mode="w", delete=False) as tmp_file:
        tmp_file.write(query)
        tmp_file_path = tmp_file.name

    command = f'pgbench { get_database_url(extension)} -f {tmp_file_path} -c {clients} -j {threads} -t {transactions} -P 5 -r'
    stdout, stderr = run_command(command)

    # Extract latency average using regular expression
    latency_average = None
    latency_average_match = re.search(
        r'latency average = (\d+\.\d+) ms', stdout)
    if latency_average_match:
        latency_average = float(latency_average_match.group(1))

    # Extract latency stddev using regular expression
    latency_stddev = None
    latency_stddev_match = re.search(r'latency stddev = (\d+\.\d+) ms', stdout)
    if latency_stddev_match:
        latency_stddev = float(latency_stddev_match.group(1))

    # Extract TPS (Transactions Per Second) using regular expression
    tps = None
    tps_match = re.search(r'tps = (\d+\.\d+)', stdout)
    if tps_match:
        tps = float(tps_match.group(1))

    return stdout, stderr, tps, latency_average, latency_stddev


def run_command(command):
    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    return output.decode(), error.decode()


def get_database_url(extension):
    """
    Get the appropriate database URL based on the extension.
    """
    base_url = os.environ["DATABASE_URL"]
    if extension is None:
        return base_url
    elif isinstance(extension, Extension):
        prefix = '/'.join(base_url.split('/')[:-1])
        database = extension.value.split('_')[0].lower()
        return prefix + '/' + database
    else:
        raise ValueError("Unknown extension: " + extension.value)
