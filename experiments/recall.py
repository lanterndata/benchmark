import os
import argparse
import psycopg2
import plotly.graph_objects as go
from scripts.delete_index import delete_index
from scripts.create_index import create_index
from utils.print import print_labels, print_row
from utils.pickle import save_pickle, fetch_pickle

DIR = 'outputs/recall'
MAX_QUERIES = 50

def get_file_name(extension, dataset, N):
    file_name = f"{DIR}/{extension}_{dataset}_{N}.pickle"
    return file_name

def generate_data(extension, dataset, N_values, K_values):
  # Establish connection
  db_connection_string = os.environ.get('DATABASE_URL')
  conn = psycopg2.connect(db_connection_string)
  cur = conn.cursor()

  print(f"about to calculate recall for extension={extension}, dataset={dataset}")
  for N in N_values:
      delete_index(dataset, N, conn=conn, cur=cur)
      create_index(extension, dataset, N, conn=conn, cur=cur)

      results = []
      print(f"about to calculate recall for extension={extension}, dataset={dataset}, N={N}")

      for K in K_values:
          base_table_name = f"{dataset}_base{N}"
          truth_table_name = f"{dataset}_truth{N}"
          query_table_name = f"{dataset}_query{N}"

          cur.execute(f"SELECT id FROM {query_table_name} LIMIT {MAX_QUERIES}")
          query_ids = cur.fetchall()

          recall_at_k_sum = 0
          for query_id, in query_ids:
              cur.execute(f"""
                  SELECT
                      CARDINALITY(ARRAY(SELECT UNNEST(base_ids) INTERSECT SELECT UNNEST(truth_ids)))
                  FROM 
                  (
                      SELECT 
                          q.id AS query_id,
                          (SELECT ARRAY_AGG(b.id ORDER BY q.v <-> b.v) FROM {base_table_name} b LIMIT {K}) AS base_ids,
                          t.indices[1:{K}] AS truth_ids
                      FROM 
                          {query_table_name} q
                      JOIN 
                          {truth_table_name} t
                      ON 
                          q.id = t.id
                  ) subquery
                  WHERE
                      query_id = {query_id}
              """)
              recall_query = cur.fetchone()[0]

              print(f"recall @ {K} for query_id {query_id}: {recall_query}")
              recall_at_k_sum += int(recall_query)

          # Calculate the average recall for this K
          recall_at_k = recall_at_k_sum / len(query_ids) / K
          print(f"recall @ {K}: {recall_at_k}")
          results.append((K, recall_at_k))

      print(f"Completed all recall for {N}")
      save_pickle(get_file_name(extension, dataset, N), results)

  cur.close()
  conn.close()

def get_N_values(extension, dataset):
    file_names = os.listdir(DIR)
    N_values = set()
    for file_name in file_names:
        if extension in file_name and dataset in file_name:
            N_values.add(file_name.split('_')[2].split('.')[0])
    return list(N_values)

def print_data(extension, dataset):
    N_values = get_N_values(extension, dataset)
    for N in N_values:
      data = fetch_pickle(get_file_name(extension, dataset, N))
      print_labels(dataset, N)
      print_labels('K', 'Recall')
      for K, recall in data:
          print_row(K, recall)
      print('\n\n')

def plot_data(extension, dataset):
    plot_items = []
    N_values = get_N_values(extension, dataset)
    for N in N_values:
        file_name = get_file_name(extension, dataset, N)
        results = fetch_pickle(file_name)
        x_values, y_values = zip(*results)
        key = f"N = {N}"
        plot_items.append((key, x_values, y_values))
    
    fig = go.Figure()
    for key, x_values, y_values in plot_items:
        fig.add_trace(go.Scatter(
            x=x_values,
            y=y_values,
            mode='lines+markers',
            name=key
        ))
    fig.update_layout(
        title=f"Recall vs. K for extension {extension} and dataset {dataset}",
        xaxis_title='Number of similar vectors retrieved (K)',
        yaxis_title='Recall (%)',
        yaxis=dict(
            range=[0, 1],  # Set y-axis range from 0 to 1
            tickformat=".0%",  # Display ticks as percentages
            hoverformat=".2%"  # Display hover labels as percentages with 2 decimal places
        )
    )
    fig.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Recall experiment")
    parser.add_argument("--dataset", type=str, choices=['sift', 'gist'], required=True, help="Output file name (required)")
    parser.add_argument('--extension', type=str, choices=['lantern', 'pgvector'], required=True, help='Extension type')
    parser.add_argument("--N", nargs='+', type=str, required=True, help="Dataset sizes")
    parser.add_argument("--K", nargs='+', required=True, type=int, help="K values")
    args = parser.parse_args()
    
    extension = args.extension
    dataset = args.dataset
    N_values = args.N
    K_values = args.K

    generate_data(extension, dataset, N_values, K_values)