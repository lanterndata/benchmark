import os
import argparse
import psycopg2
import plotly.graph_objects as go
from scripts.delete_index import delete_index
from scripts.create_index import create_index
from utils.print import print_labels, print_row
from scripts.script_utils import execute_sql, save_result, VALID_QUERY_DATASETS, VALID_EXTENSIONS, SUGGESTED_K_VALUES, get_experiment_results
from scripts.number_utils import convert_string_to_number, convert_number_to_string

METRIC_TYPE = 'recall'
MAX_QUERIES = 100

def generate_result(extension, dataset, N, K_values, index_params={}):
  db_connection_string = os.environ.get('DATABASE_URL')
  conn = psycopg2.connect(db_connection_string)
  cur = conn.cursor()

  delete_index(dataset, N, conn=conn, cur=cur)
  create_index(extension, dataset, N, index_params=index_params, conn=conn, cur=cur)

  print(f"dataset = {dataset}, extension = {extension}, N = {N}, index_params = {index_params}")
  for K in K_values:
      base_table_name = f"{dataset}_base{N}"
      truth_table_name = f"{dataset}_truth{N}"
      query_table_name = f"{dataset}_query{N}"

      query_ids = execute_sql(f"SELECT id FROM {query_table_name} LIMIT {MAX_QUERIES}", select=True)

      recall_at_k_sum = 0
      for query_id, in query_ids:
          truth_ids = execute_sql(f"""
              SELECT
                  indices[1:{K}]
              FROM
                  {truth_table_name}
              WHERE
                  id = {query_id}
          """, select_one=True)
          base_ids = list(map(lambda x: x[0], execute_sql(f"""
              SELECT
                  id - 1
              FROM
                  {base_table_name}
              ORDER BY
                  v <-> (
                      SELECT
                          v
                      FROM
                          {query_table_name}
                      WHERE
                          id = {query_id} 
                  )
              LIMIT {K}
          """, select=True)))
          recall_at_k_sum += len(set(truth_ids).intersection(base_ids))

      # Calculate the average recall for this K
      recall_at_k = recall_at_k_sum / len(query_ids) / K
      print(f"recall@{K}:".ljust(10), "{:.2f}".format(recall_at_k))
      save_result(
        metric_type='recall',
        metric_value=recall_at_k,
        database=extension,
        database_params=index_params,
        dataset=dataset,
        n=convert_string_to_number(N),
        k=K,
        conn=conn,
        cur=cur,
      )
  print()

  cur.close()
  conn.close()

def print_results(extension, dataset):
    N_values = VALID_QUERY_DATASETS[dataset]
    for N in N_values:
        results = get_experiment_results(METRIC_TYPE, extension, dataset, N)
        for index, (database_params, param_results) in enumerate(results):
            print_labels(dataset + ' - ' + convert_number_to_string(N), 'K', 'Recall')
            for K, recall in param_results:
                print_row(K, recall)
            print('\n\n')

def plot_results(extension, dataset):
    fig = go.Figure()

    N_values = VALID_QUERY_DATASETS[dataset]
    for N in N_values:
        results = get_experiment_results(METRIC_TYPE, extension, dataset, N)
        for index, (database_params, param_results) in enumerate(results):
            K_values, recalls = zip(*param_results)
            fig.add_trace(go.Scatter(
                x=K_values,
                y=recalls,
                mode='lines+markers',
                name=f"N={N} {database_params}",
                legendgroup=f"N={N}",
                legendgrouptitle={'text': f"N={N}"}
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
    parser = argparse.ArgumentParser(description="recall experiment")
    parser.add_argument("--dataset", type=str, choices=VALID_QUERY_DATASETS.keys(), required=True, help="output file name (required)")
    parser.add_argument('--extension', type=str, choices=VALID_EXTENSIONS, required=True, help='extension type')
    parser.add_argument("--N", nargs='+', type=str, help="dataset sizes")
    parser.add_argument("--K", nargs='+', type=int, help="K values")
    args = parser.parse_args()
    
    extension = args.extension
    dataset = args.dataset
    N_values = args.N or VALID_QUERY_DATASETS[dataset]
    K_values = args.K or SUGGESTED_K_VALUES

    for N in N_values:
        generate_result(extension, dataset, N, K_values)