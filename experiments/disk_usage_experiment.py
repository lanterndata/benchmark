import os
import psycopg2
import plotly.graph_objects as go
from scripts.create_index import create_index
from scripts.delete_index import delete_index
from scripts.script_utils import execute_sql, VALID_EXTENSIONS, get_index_name, save_result, get_experiment_results, parse_args
from utils.colors import get_color_from_extension
from scripts.number_utils import convert_string_to_number, convert_bytes_to_number, convert_number_to_string
from utils.print import print_labels, print_row, get_title

METRIC_TYPE = 'disk usage (bytes)'


def generate_result(extension, dataset, N, index_params={}):
    db_connection_string = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(db_connection_string)
    cur = conn.cursor()

    delete_index(extension, dataset, N, conn=conn, cur=cur)
    create_index(extension, dataset, N,
                 index_params=index_params, conn=conn, cur=cur)
    index = get_index_name(extension, dataset, N)

    execute_sql(
        f"SELECT pg_size_pretty(pg_total_relation_size('{index}'))", conn=conn, cur=cur)
    disk_usage = cur.fetchone()[0]

    save_result(
        metric_type='disk usage (bytes)',
        metric_value=convert_bytes_to_number(disk_usage),
        database=extension,
        database_params=index_params,
        dataset=dataset,
        n=convert_string_to_number(N),
        conn=conn,
        cur=cur,
    )
    print(get_title(extension, index_params, dataset, N) +
          " | disk usage: " + disk_usage)

    cur.close()
    conn.close()


def print_results(dataset):
    for extension in VALID_EXTENSIONS:
        results = get_experiment_results(METRIC_TYPE, extension, dataset)
        if len(results) == 0:
            print(f"No results for {extension}")
            print("\n\n")
        for (database_params, param_results) in results:
            print_labels(get_title(extension, database_params,
                         dataset), 'N', 'Disk Usage (MB)')
            for N, disk_usage in param_results:
                print_row(convert_number_to_string(N), disk_usage)
            print('\n\n')


def plot_results(dataset):
    fig = go.Figure()

    for extension in VALID_EXTENSIONS:
        results = get_experiment_results(METRIC_TYPE, extension, dataset)
        for index, (database_params, param_results) in enumerate(results):
            N_values, disk_usages = zip(*param_results)
            fig.add_trace(go.Scatter(
                x=N_values,
                y=disk_usages,
                marker=dict(color=get_color_from_extension(
                    extension, index=index)),
                mode='lines+markers',
                name=f"{extension} - {database_params}",
                legendgroup=extension,
                legendgrouptitle={'text': extension}
            ))
    fig.update_layout(
        title=f"Disk Usage over Data Size for {dataset}",
        xaxis=dict(title='Number of rows'),
        yaxis=dict(title='Disk Usage (bytes)'),
    )
    fig.show()


if __name__ == '__main__':
    extension, index_params, dataset, N_values, _ = parse_args(
        "disk usage experiment", ['extension', 'N'])
    for N in N_values:
        generate_result(extension, dataset, N, index_params)
