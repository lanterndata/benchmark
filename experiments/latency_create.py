import os
import argparse
import subprocess
import statistics
import plotly.graph_objects as go
from scripts.delete_index import get_drop_index_query, delete_index
from scripts.create_index import get_create_index_query
from utils.colors import get_color_from_extension
from scripts.number_utils import convert_string_to_number
from utils.print import print_labels, print_row
from utils.pickle import save_pickle, fetch_pickle

DIR = "outputs/latency_create"
SUPPRESS_COMMAND = "SET client_min_messages TO WARNING"

def get_file_name(dataset, extension):
    file_name = f"{DIR}/{dataset}_{extension}.pickle"
    return file_name

def generate_data(dataset, extensions, N_values, count=10):
    user = os.environ.get('POSTGRES_USER')
    
    for extension in extensions:
      results = []
      for N in N_values:
          delete_index(dataset, N)

          current_results = []
          for c in range(count):
              print(f"dataset: {dataset}, N: {N}, count: {c}")

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
              
          results.append((N, current_results))
      
      save_pickle(get_file_name(dataset, extension), results)
      print('\n\n')
      print_data(dataset, extensions=[extension])

def format_mean(times):
    return "{:.2f}".format(statistics.mean(times))

def format_stdev(times):
    return "{:.2f}".format(statistics.stdev(times))

def get_dir_extensions(dataset):
    file_names = os.listdir(DIR)
    extensions = list(set([file_name.split('_')[1].split('.')[0] for file_name in file_names if file_name.startswith(dataset)]))
    return extensions

def print_data(dataset, extensions=[]):
    if len(extensions) == 0:
       extensions = get_dir_extensions(dataset)
    
    for extension in extensions:
      data = fetch_pickle(get_file_name(dataset, extension))
      print_labels(f"{dataset} - {extension}", 'N', 'Time (ms)', 'Std Dev (ms)')
      for N, times in data:
          print_row(N, format_mean(times), format_stdev(times))
      print('\n\n')

def plot_data(dataset, extensions=[]):
    if len(extensions) == 0:
       extensions = get_dir_extensions(dataset)

    plot_items = []
    for extension in extensions:
      data = fetch_pickle(get_file_name(dataset, extension))
      N_values, times = zip(*data)
      x_values = list(map(convert_string_to_number, N_values))
      y_values = list(map(format_mean, times))
      plot_items.append((extension, x_values, y_values))

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
    parser.add_argument("--dataset", type=str, choices=['sift', 'gist'], required=True, help="Output file name (required)")
    parser.add_argument('--extension', nargs='+', type=str, choices=['none', 'lantern', 'pgvector'], required=True, help='Extension type')
    parser.add_argument("--N", type=str, required=True, help="Dataset sizes")
    args = parser.parse_args()
    
    extensions = args.extension
    dataset = args.dataset
    N_values = args.N

    generate_data(dataset, extensions, N_values)