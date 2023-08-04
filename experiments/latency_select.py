import os
import re
import argparse
import psycopg2
import plotly.graph_objects as go
from tempfile import NamedTemporaryFile
from scripts.delete_index import delete_index
from scripts.create_index import create_index
from scripts.script_utils import get_table_name, run_command, save_result, extract_connection_params, VALID_EXTENSIONS, VALID_DATASETS, SUGGESTED_K_VALUES, execute_sql
from utils.colors import get_color_from_extension
from scripts.number_utils import convert_string_to_number

def generate_result(extension, dataset, N, K_values):
    db_connection_string = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(db_connection_string)
    cur = conn.cursor()

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

        host, port, user, password, database = extract_connection_params(db_connection_string)
        command = f'PGPASSWORD={password} pgbench -d {database} -U {user} -h {host} -p {port} -f {tmp_file_path} -c 8 -j 8 -t 15 -r'
        stdout, stderr = run_command(command)

        result = {
            'database': extension,
            'dataset': dataset,
            'n': convert_string_to_number(N),
            'k': K,
            'out': stdout,
            'err': stderr,
            'conn': conn,
            'cur': cur,
        }

        # Extract latency average using regular expression
        latency_average = None
        latency_average_match = re.search(r'latency average = (\d+\.\d+) ms', stdout)
        if latency_average_match:
            latency_average = float(latency_average_match.group(1))
            save_result(
                metric_type='select (latency ms)',
                metric_value=latency_average,
                **result
            )

        # Extract TPS (Transactions Per Second) using regular expression
        tps = None
        tps_match = re.search(r'tps = (\d+\.\d+)', stdout)
        if tps_match:
            tps = float(tps_match.group(1))
            save_result(
                metric_type='select (tps)',
                metric_value=tps,
                **result
            )

        print(stdout)
        print(f"Finished pgbench with dataset={dataset}, N={N}, extension={extension}, K={K}\n")
    
    if extension != 'none':
        delete_index(dataset, N, conn=conn, cur=cur)

    cur.close()
    conn.close()

full_strings = {
    'N': 'Number of rows (N)',
    'K': 'Number of similar vectors (K)'
}

def generate_plot(metric_type, dataset, x_params, x, y, fixed, fixed_value):
    # Process data
    plot_items = []
    for extension in VALID_EXTENSIONS:
        x_values = []
        y_values = []
        for x_param in x_params:
            sql = f"""
                SELECT
                    metric_value
                FROM
                    experiment_results
                WHERE
                    metric_type = %s
                    AND database = %s
                    AND dataset = %s
                    AND {x} = %s
                    AND {fixed} = %s
            """
            data = (metric_type, extension, dataset, x_param, fixed_value)
            value = execute_sql(sql, data, select_one=True)
            if value is not None:
                x_values.append(x_param)
                y_values.append(value)
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

def generate_plots(dataset):
    N_values = list(map(convert_string_to_number, VALID_DATASETS[dataset]))
    generate_plot(metric_type='select (latency ms)', dataset=dataset, x_params=N_values, x='N', y='latency (ms)', fixed='K', fixed_value=5)
    generate_plot(metric_type='select (latency ms)', dataset=dataset, x_params=SUGGESTED_K_VALUES, x='K', y='latency (ms)', fixed='N', fixed_value=100000)
    generate_plot(metric_type='select (tps)', dataset=dataset, x_params=N_values, x='N', y='transactions / second', fixed='K', fixed_value=5)
    generate_plot(metric_type='select (tps)', dataset=dataset, x_params=SUGGESTED_K_VALUES, x='K', y='transactions / second', fixed='N', fixed_value=100000)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="latency select experiment")
    parser.add_argument("--dataset", type=str, choices=['sift', 'gist'], required=True, help="output file name (required)")
    parser.add_argument('--extension', nargs='+', type=str, choices=['none', 'lantern', 'pgvector'], required=True, help='extension type')
    parser.add_argument("--N", type=str, required=True, help="dataset sizes")
    parser.add_argument("--K", nargs='+', required=True, type=int, help="K values")
    args = parser.parse_args()
    
    extensions = args.extension
    dataset = args.dataset
    N_values = args.N
    K_values = args.K

    for extension in extensions:
      for N in N_values:
        generate_data(dataset, extensions, N_values, K_values)