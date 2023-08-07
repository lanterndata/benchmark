import os
import argparse
import subprocess
import statistics
import plotly.graph_objects as go
from scripts.delete_index import get_drop_index_query, delete_index
from scripts.create_index import get_create_index_query
from utils.colors import get_color_from_extension
from scripts.number_utils import convert_string_to_number, convert_number_to_string
from scripts.script_utils import save_result, VALID_EXTENSIONS, VALID_DATASETS, execute_sql, parse_args
from utils.print import print_labels, print_row

METRIC_TYPE = 'create (latency ms)'
PG_USER = os.environ.get('POSTGRES_USER')
SUPPRESS_COMMAND = "SET client_min_messages TO WARNING"

def generate_result(extension, dataset, N, index_params={}, count=10):
    delete_index(dataset, N)

    print(f"extension: {extension}, extension_params: {index_params}, dataset: {dataset}, N: {N}")
    current_results = []
    for c in range(count):
        create_index_query = get_create_index_query(extension, dataset, N, index_params)
        result = subprocess.run(["psql", "-U", PG_USER, "-c", SUPPRESS_COMMAND, "-c", "\\timing", "-c", create_index_query], capture_output=True, text=True)

        drop_index_query = get_drop_index_query(dataset, N)
        with open(os.devnull, "w") as devnull:
            subprocess.run(["psql", "-U", PG_USER, "-c", SUPPRESS_COMMAND, "-c", drop_index_query], stdout=devnull)

        lines = result.stdout.splitlines()
        for line in lines:
            if line.startswith("Time:"):
              time = float(line.split(":")[1].strip().split(" ")[0])
              current_results.append(time)
              print(f"{c} / {count}: {time} ms")
              break
    
    average_latency = statistics.mean(current_results)
    save_result(
        metric_type=METRIC_TYPE,
        metric_value=average_latency,
        database=extension,
        database_params=index_params,
        dataset=dataset,
        n=convert_string_to_number(N)
    )
    print('average latency:', average_latency, 'ms\n')

def get_n_latency(extension, dataset):
    sql = """
        SELECT DISTINCT
            database_params
        FROM
            experiment_results
        WHERE
            metric_type = %s
            AND database = %s
            AND dataset = %s
    """
    data = (METRIC_TYPE, extension, dataset)
    database_params = execute_sql(sql, data=data, select=True)
    database_params = [p[0] for p in database_params]

    values = []
    for p in database_params:
        sql = """
            SELECT
                N,
                metric_value
            FROM
                experiment_results
            WHERE
                metric_type = %s
                AND database = %s
                AND database_params = %s
                AND dataset = %s
            ORDER BY
                N
        """
        data = (METRIC_TYPE, extension, p, dataset)
        values.append((p, execute_sql(sql, data=data, select=True)))
    return values

def print_results(dataset):
    for extension in VALID_EXTENSIONS:
      results = get_n_latency(extension, dataset)
      if len(results) == 0:
          print(f"No results for {extension}")
          print("\n\n")
      for (database_params, param_results) in results:
          print_labels(f"{dataset} - {extension} - {database_params}", 'N', 'Time (ms)')
          for N, latency in param_results:
              print_row(convert_number_to_string(N), "{:.2f}".format(latency))
          print('\n\n')

def plot_results(dataset):
    fig = go.Figure()

    for extension in VALID_EXTENSIONS:
        results = get_n_latency(extension, dataset)
        for index, (database_params, param_results) in enumerate(results):
            N_values, times = zip(*param_results)
            fig.add_trace(go.Scatter(
                x=N_values,
                y=times,
                marker=dict(color=get_color_from_extension(extension, index)),
                mode='lines+markers',
                name=f"{extension} - {database_params}",
                legendgroup=extension,
                legendgrouptitle={'text': extension}
            ))
    fig.update_layout(
        title=f"Create Index Latency over Number of Rows for {dataset}",
        xaxis=dict(title='Number of rows'),
        yaxis=dict(title='Latency (ms)'),
    )
    fig.show()

if __name__ == '__main__':
    extension, index_params, dataset, N_values, _ = parse_args("create experiment", ['extension', 'N'])
    for N in N_values:
        generate_result(extension, dataset, N, index_params)