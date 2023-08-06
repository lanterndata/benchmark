import os
import argparse
import subprocess
import statistics
import plotly.graph_objects as go
from scripts.delete_index import get_drop_index_query, delete_index
from scripts.create_index import get_create_index_query
from utils.colors import get_color_from_extension
from scripts.number_utils import convert_string_to_number
from scripts.script_utils import save_result, VALID_EXTENSIONS, VALID_DATASETS
from utils.print import print_labels, print_row

SUPPRESS_COMMAND = "SET client_min_messages TO WARNING"

def generate_result(extension, dataset, N, count=10):
    user = os.environ.get('POSTGRES_USER')
    
    delete_index(dataset, N)

    current_results = []
    for c in range(count):
        print(f"extension: {extension}, dataset: {dataset}, N: {N}, count: {c} / {count}")

        create_index_query = get_create_index_query(extension, dataset, N)
        result = subprocess.run(["psql", "-U", user, "-c", SUPPRESS_COMMAND, "-c", "\\timing", "-c", create_index_query], capture_output=True, text=True)

        drop_index_query = get_drop_index_query(dataset, N)
        with open(os.devnull, "w") as devnull:
          subprocess.run(["psql", "-U", user, "-c", SUPPRESS_COMMAND, "-c", drop_index_query], stdout=devnull)

        lines = result.stdout.splitlines()
        for line in lines:
          if line.startswith("Time:"):
            time = float(line.split(":")[1].strip().split(" ")[0])
            current_results.append(time)
            break
    
    average_latency = statistics.mean(current_results)
    save_result(
        metric_type='create (latency ms)',
        metric_value=average_latency,
        database=extension,
        dataset=dataset,
        n=convert_string_to_number(N)
    )
    print('average latency:', average_latency, 'ms')

def get_n_latency(extension, dataset):
  sql = """
      SELECT
          N,
          metric_value
      FROM
          experiment_results
      WHERE
          metric_type = 'create (latency ms)'
          AND database = %s
          AND dataset = %s
      ORDER BY
          N
  """
  data = (extension, dataset)
  values = execute_sql(sql, data=data, select=True)
  return values

def print_results(dataset):
    for extension in VALID_EXTENSIONS:
      results = get_n_latency(extension, dataset)
      if len(results) == 0:
          continue
      print_labels(f"{dataset} - {extension}", 'N', 'Time (ms)')
      for N, times in data:
          print_row(N, "{:.2f}".format(latency))
      print('\n\n')

def plot_results(dataset):
    plot_items = []
    for extension in VALID_EXTENSIONS:
      results = get_n_latency(extension, dataset)
      if len(results) == 0:
          continue
      N_values, times = zip(*results)
      plot_items.append((extension, N_values, times))

    fig = go.Figure()
    for (extension, x_values, y_values) in plot_items:
        fig.add_trace(go.Scatter(
            x=x_values,
            y=y_values,
            marker=dict(color=get_color_from_extension(extension)),
            mode='lines+markers',
            name=extension
        ))
    fig.update_layout(
        title=f"Create Index Latency over Number of Rows for {dataset}",
        xaxis=dict(title='Number of rows'),
        yaxis=dict(title='Latency (ms)'),
    )
    fig.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Latency create experiment")
    parser.add_argument("--dataset", type=str, choices=VALID_DATASETS.keys(), required=True, help="Output file name (required)")
    parser.add_argument('--extension', type=str, choices=VALID_EXTENSIONS, required=True, help='Extension type')
    parser.add_argument("--N", nargs='+', type=str, help="Dataset sizes")
    args = parser.parse_args()
    
    extension = args.extension
    dataset = args.dataset
    N_values = args.N or VALID_DATASETS[dataset]

    for N in N_values:
        generate_result(extension, dataset, N)