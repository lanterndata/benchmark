import os
import re
import argparse
import psycopg2
import plotly.graph_objects as go
from tempfile import NamedTemporaryFile
from scripts.delete_index import delete_index
from scripts.create_index import create_index
from scripts.script_utils import get_table_name, run_command, extract_connection_params
from utils.colors import get_color_from_extension
from utils.numbers import convert_number_to_string, convert_string_to_number

DIR = 'outputs/latency_select'

def get_pgbench_file_name(extension, dataset, N, K, error=False):
    return f"{DIR}/{dataset}_{extension}_{N}_K{K}{'_error' if error else ''}.txt"

def generate_data(dataset, extensions, N_values, K_values):
    db_connection_string = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(db_connection_string)
    cur = conn.cursor()

    for extension in extensions:
      for N in N_values:
          delete_index(dataset, N, conn=conn, cur=cur)
          if extension != 'none':
              create_index(extension, dataset, N, conn=conn, cur=cur)

          for K in K_values:
              table = get_table_name(dataset, N)
              query = f"""
                  \set id random(1, 10000)
      
                  SELECT *
                  FROM {table}
                  ORDER BY v <-> (
                      SELECT v
                      FROM {table}
                      WHERE id = :id
                  )
                  LIMIT {K};
              """
              with NamedTemporaryFile(mode="w", delete=False) as tmp_file:
                  tmp_file.write(query)
                  tmp_file_path = tmp_file.name

              output_file = get_pgbench_file_name(extension, dataset, N, K)
              error_file = get_pgbench_file_name(extension, dataset, N, K, error=True)
              host, port, user, password, database = extract_connection_params(db_connection_string)
              command = f'PGPASSWORD={password} pgbench -d {database} -U {user} -h {host} -p {port} -f {tmp_file_path} -c 5 -j 5 -t 15 -r > {output_file} 2>{error_file}'
              run_command(command)

              with open(output_file, "r") as file:
                  print(file.read())
              print(f"Finished pgbench with dataset={dataset}, N={N}, extension={extension}, K={K}\n")
          
          if extension != 'none':
              delete_index(dataset, N, conn=conn, cur=cur)

    cur.close()
    conn.close()

def parse_data(dataset):
    N_values = set()
    K_values = set()
    extensions = set()

    latency_values = {}
    tps_values = {}

    file_names = os.listdir(DIR)

    for file_name in file_names:
        if dataset not in file_name:
            continue
        key = file_name.split('.')[0]
        parts = key.split('_')
        if len(parts) != 4:
            continue
        extensions.add(parts[1])
        N_values.add(convert_string_to_number(parts[2]))
        K_values.add(int(parts[3][1:]))

        # Read the file and extract the latency average value
        with open(f"{DIR}/{file_name}", 'r') as file:
            file_content = file.read()

            # Extract latency average using regular expression
            latency_average_match = re.search(r'latency average = (\d+\.\d+) ms', file_content)
            if latency_average_match:
                latency_values[key] = float(latency_average_match.group(1))

            # Extract TPS (Transactions Per Second) using regular expression
            tps_match = re.search(r'tps = (\d+\.\d+)', file_content)
            if tps_match:
                tps_values[key] = float(tps_match.group(1))
    
    extensions = list(filter(lambda e: e in extensions, ['lantern', 'pgvector', 'none']))
    N_values = sorted(list(N_values))
    K_values = sorted(list(K_values))

    return extensions, N_values, K_values, latency_values, tps_values

full_strings = {
    'N': 'Number of rows (N)',
    'K': 'Number of similar vectors (K)'
}

def generate_plot(dataset, param_values, x, y, key_to_values_dict, fixed, fixed_value):
    # Process data
    plot_items = []
    for extension in param_values['extensions']:
        x_values = []
        y_values = []
        for param_x in param_values[x]:
            key_params = {}
            key_params[x] = param_x
            key_params[fixed] = fixed_value

            pgbench_file_name = get_pgbench_file_name(extension, dataset, convert_number_to_string(key_params['N']), key_params['K'])
            key = pgbench_file_name.split('.')[0].split('/')[-1]
            if key in key_to_values_dict:
                x_values.append(param_x)
                y_values.append(key_to_values_dict[key])
        if len(x_values) > 0:
            color = get_color_from_extension(extension)
            plot_items.append((extension, x_values, y_values, color))

    # Plot data
    fig = go.Figure()
    for (key, x_values, y_values, color) in plot_items:
        fig.add_trace(go.Scatter(
            x=x_values,
            y=y_values,
            marker=dict(color=color),
            mode='lines+markers',
            name=key
        ))
    fig.update_layout(
        title=f"{y} vs. {x}",
        xaxis_title=full_strings[x],
        yaxis_title=y
    )
    fig.show()

def plot_data(dataset):
    extensions, N_values, K_values, latency_values, tps_values = parse_data(dataset)
    param_values = {
        'extensions': extensions,
        'N': N_values,
        'K': K_values
    }
    generate_plot(dataset, param_values, x='N', y='Latency (ms)', key_to_values_dict=latency_values, fixed='K', fixed_value=4)
    generate_plot(dataset, param_values, x='K', y='Latency (ms)', key_to_values_dict=latency_values, fixed='N', fixed_value=100000)
    generate_plot(dataset, param_values, x='N', y='Transactions / second', key_to_values_dict=tps_values, fixed='K', fixed_value=4)
    generate_plot(dataset, param_values, x='K', y='Transactions / second', key_to_values_dict=tps_values, fixed='N', fixed_value=100000)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Latency select experiment")
    parser.add_argument("--dataset", type=str, choices=['sift', 'gist'], required=True, help="Output file name (required)")
    parser.add_argument('--extension', nargs='+', type=str, choices=['none', 'lantern', 'pgvector'], required=True, help='Extension type')
    parser.add_argument("--N", type=str, required=True, help="Dataset sizes")
    parser.add_argument("--K", nargs='+', required=True, type=int, help="K values")
    args = parser.parse_args()
    
    extensions = args.extension
    dataset = args.dataset
    N_values = args.N
    K_values = args.K

    generate_data(dataset, extensions, N_values, K_values)