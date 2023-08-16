import os
import csv
import json
from .numbers import convert_string_to_number
from .database import DatabaseConnection


def _get_metric_type_sql(metric_type):
    if isinstance(metric_type, str):
        return 'metric_type = %s'
    else:
        return 'metric_type = ANY(%s)'


def get_distinct_index_params(metric_type, extension, dataset, N=None):
    n_sql = '' if N is None else 'AND N = %s'
    metric_type_sql = _get_metric_type_sql(metric_type)
    sql = f"""
        SELECT DISTINCT
            index_params
        FROM
            experiment_results
        WHERE
            {metric_type_sql}
            AND extension = %s
            AND dataset = %s
            {n_sql}
    """
    data = (metric_type, extension, dataset)
    if N is not None:
        data += (convert_string_to_number(N),)
    with DatabaseConnection(extension) as conn:
        index_params = conn.select(sql, data=data)
    index_params = [p[0] for p in index_params]
    return index_params


def get_experiment_results_for_params(metric_type, extension, index_params, dataset, N=None):
    x_param = 'N' if N is None else 'K'
    n_sql = '' if N is None else 'AND N = %s'
    sql = f"""
        SELECT
            {x_param},
            metric_value
        FROM
            experiment_results
        WHERE
            metric_type = %s
            AND extension = %s
            AND index_params = %s
            AND dataset = %s
            {n_sql}
        ORDER BY
            {x_param}
    """
    data = (metric_type, extension, index_params, dataset)
    if N is not None:
        data += (convert_string_to_number(N),)
    with DatabaseConnection(extension) as conn:
        results = conn.select(sql, data=data)
    return results


def get_experiment_results(metric_type, extension, dataset, N=None):
    index_params = get_distinct_index_params(
        metric_type, extension, dataset, N)
    values = []
    for p in index_params:
        value = get_experiment_results_for_params(
            metric_type, extension, p, dataset, N)
        values.append((p, value))
    return values


TABLE_COLUMNS = ['extension', 'index_params', 'dataset',
                 'n', 'k', 'metric_type', 'metric_value', 'out', 'err']


def dump_results_to_csv():
    sql = f"""
        SELECT
            {', '.join(TABLE_COLUMNS[:-2])}
        FROM
            experiment_results
        ORDER BY
            metric_type,
            extension,
            dataset
    """
    with DatabaseConnection() as conn:
        rows = conn.select(sql)

    script_directory = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_directory, "../outputs/results.csv")

    with open(output_file, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(TABLE_COLUMNS[:-2])
        for row in rows:
            csv_writer.writerow(row)


def save_result(metric_type, metric_value, extension, index_params, dataset, n, k=0, out=None, err=None):
    columns = ', '.join(TABLE_COLUMNS)
    placeholders = ', '.join(['%s'] * len(TABLE_COLUMNS))
    updates = ', '.join(
        map(lambda col: f"{col} = EXCLUDED.{col}", TABLE_COLUMNS))

    sql = f"""
        INSERT INTO
            experiment_results ({columns})
        VALUES
            ({placeholders})
        ON CONFLICT ON CONSTRAINT
            unique_result
        DO UPDATE SET
            {updates}
    """

    data = (TABLE_COLUMNS, json.dumps(index_params), dataset,
            n, k, metric_type, metric_value, out, err)

    with DatabaseConnection(extension) as conn:
        conn.execute(sql, data=data)

    dump_results_to_csv()
