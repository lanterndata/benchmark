import os
import re
import sys
import psycopg2
import plotly.graph_objects as go
from tempfile import NamedTemporaryFile
from scripts.delete_index import delete_index
from scripts.create_index import create_index
from scripts.script_utils import get_table_name, green_shades, red_shades, save_data, fetch_data, convert_number_to_string, convert_string_to_number, extract_connection_params, run_command

DIR = 'outputs/latency_select'

def get_file_name(dataset):
    file_name = f"{DIR}/{dataset}.pickle"
    return file_name

def get_pgbench_file_name(dataset, N, K, should_index):
    should_index_str = 'true' if should_index else 'false'
    return f"{DIR}/{dataset}_{should_index_str}_{N}_K{K}.txt"

def parse_data(dataset):
    N_values = set()
    K_values = set()

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
    
    N_values = sorted(list(N_values))
    K_values = sorted(list(K_values))

    return N_values, K_values, latency_values, tps_values

def generate_data(dataset, N_values, K_values, should_index_values=[False, True]):
    db_connection_string = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(db_connection_string)
    cur = conn.cursor()

    for should_index in should_index_values:
      for N in N_values:
          delete_index(dataset, N, conn=conn, cur=cur)
          if should_index:
              create_index(dataset, N, conn=conn, cur=cur)
      print(f"Indices {'created' if should_index else 'deleted'}")

      for N in N_values:
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

              output_file = get_pgbench_file_name(dataset, N, K, should_index)
              host, port, user, password, database = extract_connection_params(db_connection_string)
              command = f'PGPASSWORD={password} pgbench -d {database} -U {user} -h {host} -p {port} -f {tmp_file_path} -c 5 -j 5 -t 15 -r > {output_file} 2>/dev/null'
              run_command(command)

              with open(output_file, "r") as file:
                  print(file.read())
              print(f"Finished pgbench with dataset={dataset}, N={N}, indexed={should_index}, K={K}\n")
          
          if should_index:
              delete_index(dataset, N, conn=conn, cur=cur)

    cur.close()
    conn.close()

    data = parse_data(dataset)
    save_data(get_file_name(dataset), data)

full_strings = {
    'N': 'Number of rows (N)',
    'K': 'Number of similar vectors (K)'
}

def generate_plot(dataset, param_values, x, y, key_to_values_dict, fixed, fixed_value):
    # Process data
    plot_items = []
    for indexed in [True, False]:
        x_values = []
        y_values = []
        for param_x in param_values[x]:
            key_params = {}
            key_params[x] = param_x
            key_params[fixed] = fixed_value

            key = get_pgbench_file_name(dataset, convert_number_to_string(key_params['N']), key_params['K'], indexed).split('.')[0].split('/')[-1]
            if key in key_to_values_dict:
                x_values.append(param_x)
                y_values.append(key_to_values_dict[key])
        if len(x_values) > 0:
            if indexed:
                indexed_str = 'indexed'
                color = green_shades[0]
            else:
                indexed_str = 'unindexed'
                color = red_shades[0]

            plot_items.append((f"{indexed_str}", x_values, y_values, color))

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
    data = parse_data(dataset)
    save_data(get_file_name(dataset), data)

    N_values, K_values, latency_values, tps_values = fetch_data(get_file_name(dataset))
    param_values = {
        'N': N_values,
        'K': K_values
    }
    generate_plot(dataset, param_values, x='N', y='Latency (ms)', key_to_values_dict=latency_values, fixed='K', fixed_value=4)
    generate_plot(dataset, param_values, x='K', y='Latency (ms)', key_to_values_dict=latency_values, fixed='N', fixed_value=100000)
    generate_plot(dataset, param_values, x='N', y='Transactions / second', key_to_values_dict=tps_values, fixed='K', fixed_value=4)
    generate_plot(dataset, param_values, x='K', y='Transactions / second', key_to_values_dict=tps_values, fixed='N', fixed_value=100000)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise Exception('Usage: python latency_select.py sift 10k,100k,1m, 1,2,4,8')

    dataset = sys.argv[1]
    N_values = sys.argv[2].split(',')
    K_values = map(int, sys.argv[3].split(','))
    generate_data(dataset, N_values, K_values)