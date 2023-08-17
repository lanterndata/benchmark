import subprocess
import statistics
import plotly.graph_objects as go
from utils.database import get_database_url
from utils.delete_index import delete_index
from utils.create_index import get_create_index_query
from utils.colors import get_color_from_extension
from utils.numbers import convert_string_to_number, convert_number_to_string
from utils.constants import Metric, VALID_EXTENSIONS
from utils.cli import parse_args
from utils.process import save_result, get_experiment_results
from utils.print import print_labels, print_row, get_title

SUPPRESS_COMMAND = "SET client_min_messages TO WARNING"


def generate_result(extension, dataset, N, index_params={}, count=10):
    delete_index(extension, dataset, N)

    print(get_title(extension, index_params, dataset, N))
    current_results = []
    for c in range(count):
        create_index_query = get_create_index_query(
            extension, dataset, N, index_params)
        result = subprocess.run(["psql", get_database_url(extension), "-c", SUPPRESS_COMMAND, "-c",
                                "\\timing", "-c", create_index_query], capture_output=True, text=True)

        delete_index(extension, dataset, N)

        lines = result.stdout.splitlines()
        for line in lines:
            if line.startswith("Time:"):
                time = float(line.split(":")[1].strip().split(" ")[0])
                current_results.append(time)
                print(f"{c} / {count}: {time:.2f} ms")
                break

    latency_average = statistics.mean(current_results)
    latency_stddev = statistics.stdev(current_results)

    save_result_params = {
        'extension': extension,
        'index_params': index_params,
        'dataset': dataset,
        'n': convert_string_to_number(N),
    }

    save_result(
        metric_type=Metric.CREATE_LATENCY,
        metric_value=latency_average,
        **save_result_params
    )
    save_result(
        metric_type=Metric.CREATE_LATENCY_STDDEV,
        metric_value=latency_stddev,
        **save_result_params
    )

    print('average latency:',  f"{latency_average:.2f} ms")
    print('stddev latency', f"{latency_stddev:.2f} ms")
    print()

    delete_index(extension, dataset, N)


def print_results(dataset):
    for extension in VALID_EXTENSIONS:
        results = get_experiment_results(
            [Metric.CREATE_LATENCY, Metric.CREATE_LATENCY_STDDEV], extension, dataset)
        if len(results) == 0:
            print(f"No results for {extension}")
            print("\n\n")
        for (index_params, param_results) in results:
            print(get_title(extension, index_params, dataset))
            print_labels('N', 'Avg time (ms)', print('Stddev time (ms)'))
            for N, average, stddev in param_results:
                print_row(
                    convert_number_to_string(N),
                    "{:.2f}".format(average),
                    "{:.2f}".format(stddev)
                )
            print('\n\n')


def plot_results(dataset):
    fig = go.Figure()

    for extension in VALID_EXTENSIONS:
        results = get_experiment_results(
            Metric.CREATE_LATENCY, extension, dataset)
        for index, (index_params, param_results) in enumerate(results):
            N_values, times = zip(*param_results)
            fig.add_trace(go.Scatter(
                x=N_values,
                y=times,
                marker=dict(color=get_color_from_extension(extension, index)),
                mode='lines+markers',
                name=f"{extension.value.upper()} - {index_params}",
                legendgroup=extension.value.upper(),
                legendgrouptitle={'text': extension.value.upper()}
            ))
    fig.update_layout(
        title=f"Create Index Latency over Number of Rows for {dataset.value}",
        xaxis=dict(title='Number of rows'),
        yaxis=dict(title='Latency (ms)'),
    )
    fig.show()


if __name__ == '__main__':
    extension, index_params, dataset, N_values, _ = parse_args(
        "create experiment", ['extension', 'N'])
    for N in N_values:
        generate_result(extension, dataset, N, index_params)
