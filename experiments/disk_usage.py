import os
import argparse
import psycopg2
import plotly.graph_objects as go
from scripts.create_index import create_index
from scripts.delete_index import delete_index
from scripts.script_utils import execute_sql
from utils.colors import get_color_from_extension
from scripts.number_utils import convert_string_to_number, convert_bytes_to_number
from utils.print import print_labels, print_row
from utils.pickle import save_pickle, fetch_pickle

DIR = 'outputs/disk'

def get_file_name(dataset, extension):
    file_name = f"{DIR}/{dataset}_{extension}.pickle"
    return file_name

def generate_data(dataset, extensions, N_values):
    db_connection_string = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(db_connection_string)
    cur = conn.cursor()
    
    for extension in extensions:
      disk_usages = []
      print_labels(f"{dataset} - {extension}", 'N', 'Disk Usage (MB)')
      for N in N_values:
          delete_index(dataset, N, conn=conn, cur=cur)
          index = create_index(extension, dataset, N, conn=conn, cur=cur)
          execute_sql(f"SELECT pg_size_pretty(pg_total_relation_size('{index}'))", conn=conn, cur=cur)
          disk_usage = cur.fetchone()[0]
          disk_usages.append((N, disk_usage))
          print_row(N, disk_usage)
      print('\n\n')
      save_pickle(get_file_name(dataset, extension), disk_usages)
    
    cur.close()
    conn.close()

def print_data(dataset):
    file_names = os.listdir(DIR)
    for file_name in file_names:
      if not file_name.startswith(dataset):
          continue
      data = fetch_pickle(DIR + '/' + file_name)
      print_labels(file_name.replace('_', ' - '))
      print_labels('N', 'Disk Usage (MB)')
      for N, disk_usage in data:
          print_row(N, disk_usage)
      print('\n\n')

def plot_data(dataset):
    plot_items = []

    file_names = os.listdir(DIR)
    for file_name in file_names:
      if not file_name.startswith(dataset):
          continue
      data = fetch_pickle(DIR + '/' + file_name)
      extension = file_name.split('_')[-1].split('.')[0]
      N_values, disk_usages = zip(*data)
      x_values = list(map(convert_string_to_number, N_values))
      y_values = list(map(convert_bytes_to_number, disk_usages))
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
        title=f"Disk Usage over Data Size for {dataset}",
        xaxis=dict(title='Data Size (bytes)'),
        yaxis=dict(title='Disk Usage (MB)'),
    )
    fig.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Disk usage experiment")
    parser.add_argument("--dataset", type=str, choices=['sift', 'gist'], required=True, help="Output file name (required)")
    parser.add_argument('--extension', nargs='+', type=str, choices=['none', 'lantern', 'pgvector'], required=True, help='Extension type')
    parser.add_argument("--N", nargs='+', type=str, required=True, help="Dataset sizes")
    args = parser.parse_args()

    dataset = args.dataset
    extensions = args.extension
    N_values = args.N
    
    generate_data(dataset, extensions, N_values)