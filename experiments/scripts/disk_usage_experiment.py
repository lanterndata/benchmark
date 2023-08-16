import plotly.graph_objects as go
from utils.create_index import create_index
from utils.delete_index import delete_index
from utils.database import DatabaseConnection
from utils.cli import parse_args
from utils.names import get_index_name
from utils.constants import VALID_EXTENSIONS, Metric
from utils.process import save_result, get_experiment_results
from utils.colors import get_color_from_extension
from utils.numbers import convert_string_to_number, convert_bytes_to_number, convert_number_to_string
from utils.print import print_labels, print_row, get_title


def generate_result(extension, dataset, N, index_params={}):
    delete_index(extension, dataset, N)
    create_index(extension, dataset, N, index_params=index_params)
    index = get_index_name(dataset, N)

    with DatabaseConnection(extension) as conn:
        sql = f"SELECT pg_size_pretty(pg_total_relation_size('{index}'))"
        disk_usage = conn.select_one(sql)[0]

    save_result(
        metric_type='disk usage (bytes)',
        metric_value=convert_bytes_to_number(disk_usage),
        extension=extension,
        index_params=index_params,
        dataset=dataset,
        n=convert_string_to_number(N)
    )

    print(get_title(extension, index_params, dataset, N) +
          " | disk usage: " + disk_usage)


def print_results(dataset):
    for extension in VALID_EXTENSIONS:
        results = get_experiment_results(Metric.DISK_USAGE, extension, dataset)

        if len(results) == 0:
            print(f"No results for {extension}")
            print("\n\n")

        for (index_params, param_results) in results:
            print(get_title(extension, index_params, dataset))
            print_labels('N', 'Disk Usage (MB)')
            for N, disk_usage in param_results:
                print_row(convert_number_to_string(N), disk_usage)
            print('\n\n')


def plot_results(dataset):
    fig = go.Figure()

    for extension in VALID_EXTENSIONS:
        results = get_experiment_results(Metric.DISK_USAGE, extension, dataset)
        for index, (index_params, param_results) in enumerate(results):
            N_values, disk_usages = zip(*param_results)
            fig.add_trace(go.Scatter(
                x=N_values,
                y=disk_usages,
                marker=dict(color=get_color_from_extension(
                    extension, index=index)),
                mode='lines+markers',
                name=f"{extension} - {index_params}",
                legendgroup=extension,
                legendgrouptitle={'text': extension}
            ))
    fig.update_layout(
        title=f"Disk Usage over Data Size for {dataset.value}",
        xaxis=dict(title='Number of rows'),
        yaxis=dict(title='Disk Usage (bytes)'),
    )
    fig.show()


if __name__ == '__main__':
    extension, index_params, dataset, N_values, _ = parse_args(
        "disk usage experiment", ['extension', 'N'])
    for N in N_values:
        generate_result(extension, dataset, N, index_params)
