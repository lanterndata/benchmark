import os
import sys
import psycopg2
import plotly.graph_objects as go
from scripts.delete_index import delete_index
from scripts.create_index import create_index
from scripts.script_utils import print_labels, print_row, save_data, fetch_data, convert_string_to_number, convert_number_to_string

def get_file_name(dataset, N, max_queries=None):
    if max_queries is not None:
        file_name = f"outputs/recall/{dataset}_{N}_{max_queries}.pickle"
    else:
        file_names = os.listdir('outputs/recall')
        file_names = [f for f in file_names if f.startswith(dataset + '_' + N) and f.endswith('.pickle')].sort_by(lambda f: int(f.split('_')[2]))
        file_name = max(file_names, key=os.path.getctime)
    return file_name

def generate_data(dataset, N_values, K_values, max_queries = 100):
  # Establish connection
  db_connection_string = os.environ.get('DATABASE_URL')
  conn = psycopg2.connect(db_connection_string)
  cur = conn.cursor()

  for N in N_values:
      delete_index(dataset, N, conn=conn, cur=cur)
      create_index(dataset, N, conn=conn, cur=cur)
  print("created indices")

  print(f"about to calculate recall for dataset={dataset}")
  for N in N_values:
      results = []
      print(f"about to calculate recall for dataset={dataset}, N={N}")

      for K in K_values:
          base_table_name = f"{dataset}_base{N}"
          truth_table_name = f"{dataset}_truth{N}"
          query_table_name = f"{dataset}_query{N}"

          cur.execute(f"SELECT id FROM sift_query{N}")
          query_ids = cur.fetchall()[:max_queries]

          recall_at_k_sum = 0
          for query_id in query_ids:
              query_id = query_id[0]
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
          recall_at_k = recall_at_k_sum / len(query_ids)
          print(f"recall @ {K}: {recall_at_k}")
          results.append((K, recall_at_k))
              

      print(f"Completed all recall for {N}")
      save_data(get_file_name(dataset, N, max_queries), results)

  cur.close()
  conn.close()

def get_N_values(dataset):
    file_names = os.listdir(dir)
    N_values = set()
    for file_name in file_names:
        if dataset in file_name:
            N_values.add(file_name.split('_')[1])
    return list(N_values)

def print_data(dataset):
    N_values = get_N_values(dataset)
    for N in N_values:
      data = fetch_data(get_file_name(dataset, N))
      print_labels(dataset, N)
      print_labels('K', 'Recall')
      for K, recall in data:
          print_row(K, recall)
      print('\n\n')

def plot_data(dataset):
    N_values = get_N_values(dataset)
    N_and_file_names = [(N, get_file_name(dataset, N)) for N in N_values]
    
    plot_items = []
    for N, file_name in N_and_file_names:
        results = fetch_data(file_name)
        x_values, y_values = zip(*results)
        plot_items.append((key, x_values, y_values))
    
    # Plot data
    fig = go.Figure()
    for (key, x_values, y_values) in plot_items:
        fig.add_trace(go.Scatter(
            x=x_values,
            y=y_values,
            mode='lines+markers',
            name=key
        ))

    fig.update_layout(
        title=f"Recall vs. K for dataset {dataset}",
        xaxis_title='Number of similar vectors retrieved (K)',
        yaxis_title='Recall'
    )
    fig.show()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise Exception('Usage: python recall.py sift 10k,1m 1,2,4,8')
    
    dataset = sys.argv[1]
    N_values = sys.argv[2].split(',')
    K_values = map(int, sys.argv[3].split(','))
    generate_data(dataset, N_values, K_values)