import os
import sys
import subprocess
import statistics
import plotly.graph_objects as go
from scripts.delete_index import delete_index
from scripts.script_utils import print_labels, print_row, save_data, fetch_data, convert_string_to_number

def get_file_name(dataset):
    file_name = f"outputs/latency_create/{dataset}.pickle"
    return file_name

def generate_data(dataset, N_values, count=10):
    port = os.environ.get('POSTGRES_PORT')
    user = os.environ.get('POSTGRES_USER')
    password = "postgres"

    suppress_command = "SET client_min_messages TO WARNING"
    
    for N in N_values:
        delete_index('sift', N)
    
    results = []
    for N in N_values:
        current_results = []

        for c in range(count):
            print(f"Experiment - dataset: {dataset}, N: {N}, count: {c}")

            create_index_query = f"CREATE INDEX sift_base{N}_index ON sift_base10k USING ivfflat (v vector_l2_ops) WITH (lists = 10)"
            result = subprocess.run(["psql", "-p", port, "-U", user, "-c", suppress_command, "-c", "\\timing", "-c", create_index_query], env={"PGPASSWORD": password}, capture_output=True, text=True)

            drop_index_query = f"DROP INDEX sift_base{N}_index"
            with open(os.devnull, "w") as devnull:
              subprocess.run(["psql", "-p", port, "-U", user, "-c", suppress_command, "-c", drop_index_query], env={"PGPASSWORD": password}, stdout=devnull)

            lines = result.stdout.splitlines()
            for line in lines:
              if line.startswith("Time:"):
                time = float(line.split(":")[1].strip().split(" ")[0])
                current_results.append(time)
                break
            
        results.append((N, current_results))
    
    save_data(get_file_name(dataset), results)

    print('\n\n')
    print_data(dataset)

def format_mean(times):
    return "{:.2f}".format(statistics.mean(times))

def format_stdev(times):
    return "{:.2f}".format(statistics.stdev(times))

def print_data(dataset):
    data = fetch_data(get_file_name(dataset))
    print_labels(dataset, 'N', 'Time (ms)', 'Std Dev (ms)')
    for N, times in data:
        print_row(N, format_mean(times), format_stdev(times))
    print('\n\n')

def plot_data(dataset):
    data = fetch_data(get_file_name(dataset))
    N_values, times = zip(*data)
    x_values = list(map(convert_string_to_number, N_values))
    y_values = list(map(format_mean, times))
    y_stdev = list(map(format_stdev, times))
    error_y = dict(type='data', array=y_stdev, visible=True)

    fig = go.Figure(data=go.Scatter(x=x_values, y=y_values, error_y=error_y, mode='lines'))
    fig.update_layout(
        title=f"Create Index Latency over Number of Rows for {dataset}",
        xaxis=dict(title='Number of rows'),
        yaxis=dict(title='Latency (ms)'),
    )
    fig.show()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise Exception('Usage: python latency_create.py sift 10k,100k,1m')
    
    dataset = sys.argv[1]
    N_values = sys.argv[2].split(',')
    generate_data(dataset, N_values)