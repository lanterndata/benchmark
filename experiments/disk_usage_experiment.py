import os
import argparse
import psycopg2
import plotly.graph_objects as go
from scripts.create_index import create_index
from scripts.delete_index import delete_index
from scripts.script_utils import execute_sql, VALID_DATASETS, VALID_EXTENSIONS, get_index_name, save_result
from utils.colors import get_color_from_extension
from scripts.number_utils import convert_string_to_number, convert_bytes_to_number, convert_number_to_string
from utils.print import print_labels, print_row

def generate_result(extension, dataset, N):
    db_connection_string = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(db_connection_string)
    cur = conn.cursor()

    delete_index(dataset, N, conn=conn, cur=cur)
    create_index(extension, dataset, N, conn=conn, cur=cur)
    index = get_index_name(dataset, N)
    execute_sql(f"SELECT pg_size_pretty(pg_total_relation_size('{index}'))", conn=conn, cur=cur)
    disk_usage = cur.fetchone()[0]
    save_result(
        metric_type='disk usage (bytes)',
        metric_value=convert_bytes_to_number(disk_usage),
        database=extension,
        dataset=dataset,
        n=convert_string_to_number(N),
        conn=conn,
        cur=cur,
    )
    print(f"dataset={dataset}, extension={extension}, N={N} | disk usage {disk_usage}")
    
    cur.close()
    conn.close()

def get_n_disk_usage(extension, dataset):
  sql = """
      SELECT
          N,
          metric_value
      FROM
          experiment_results
      WHERE
          metric_type = 'disk usage (bytes)'
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
      results = get_n_disk_usage(extension, dataset)
      if len(results) == 0:
          continue
      print_labels(dataset + ' - ' + extension, 'N', 'Disk Usage (MB)')
      for N, disk_usage in data:
          print_row(convert_number_to_string(N), disk_usage)
      print('\n\n')

def plot_results(dataset):
    plot_items = []
    for extension in VALID_EXTENSIONS:
      results = get_n_disk_usage(extension, dataset)
      if len(results) == 0:
          continue
      N_values, disk_usages = zip(*results)
      plot_items.append((extension, N_values, disk_usages))
    
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
    parser = argparse.ArgumentParser(description="disk usage experiment")
    parser.add_argument("--dataset", type=str, choices=VALID_DATASETS.keys(), required=True, help="output file name (required)")
    parser.add_argument('--extension', type=str, choices=VALID_EXTENSIONS, required=True, help='extension type')
    parser.add_argument("--N", nargs='+', type=str, help="dataset sizes")
    args = parser.parse_args()

    dataset = args.dataset
    extension = args.extension
    N_values = args.N or VALID_DATASETS[dataset]
    
    for N in N_values:
        generate_result(extension, dataset, N)