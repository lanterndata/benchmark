import os
import argparse
import psycopg2
import plotly.graph_objects as go
from scripts.delete_index import delete_index
from scripts.create_index import create_index
from utils.print import print_labels, print_row
from scripts.script_utils import execute_sql, save_result
from scripts.number_utils import convert_string_to_number

MAX_QUERIES = 50

def generate_result(extension, dataset, N, K_values):
  # Establish connection
  db_connection_string = os.environ.get('DATABASE_URL')
  conn = psycopg2.connect(db_connection_string)
  cur = conn.cursor()

  delete_index(dataset, N, conn=conn, cur=cur)
  create_index(extension, dataset, N, conn=conn, cur=cur)

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
          recall_at_k_sum += int(recall_query)

      # Calculate the average recall for this K
      recall_at_k = recall_at_k_sum / len(query_ids) / K
      print(f"dataset={dataset}, extension={extension}, N={N} | recall @ {K}: {recall_at_k}")
      save_result(
        metric_type='recall',
        metric_value=recall_at_k,
        database=extension,
        dataset=dataset,
        n=convert_string_to_number(N),
        k=K,
        conn=conn,
        cur=cur,
      )

  cur.close()
  conn.close()

def get_k_recall(extension, dataset, N):
    sql = """
        SELECT
            K,
            recall
        FROM
            experiment_results
        WHERE
            metric_type = 'recall'
            AND extension = %s
            AND dataset = %s
            AND N = %s
        ORDER BY
            K
    """
    data = (extension, dataset, N)
    values = execute_sql(sql, data)
    return values

def print_results(extension, dataset):
    for N in N_values:
      results = get_k_recall(extension, dataset, N)
      print_labels(dataset, N)
      print_labels('K', 'Recall')
      for K, recall in results:
          print_row(K, recall)
      print('\n\n')

def plot_results(extension, dataset):
    plot_items = []
    for N in N_values:
        results = get_k_recall(extension, dataset, N)
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