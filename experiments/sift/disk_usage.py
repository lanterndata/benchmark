import sys
import os
import psycopg2
import pickle
from scripts.create_index import create_index
from scripts.script_utils import execute_sql, convert_string_to_number, convert_bytes_to_number
import plotly.graph_objects as go

def print_labels(dataset):
    print(dataset)
    print('-' * 20)
    print('N'.ljust(10) + 'Disk Usage')
    print('-' * 20)

def print_row(N, disk_usage):
    print(N.ljust(10) + disk_usage)

def get_file_name(dataset):
    file_name = f"outputs/disk/{dataset}.pickle"
    return file_name

def save_data(dataset, data):
    file_name = get_file_name(dataset)
    with open(file_name, 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

def fetch_data(dataset):
    file_name = get_file_name(dataset)
    if not os.path.exists(file_name):
        raise FileNotFoundError(f"There is no experiment run for dataset {dataset}")
    with open(file_name, 'rb') as handle:
        return pickle.load(handle)

def generate_data(dataset, N_values):
    # Connect to database
    db_connection_string = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(db_connection_string)
    cur = conn.cursor()
    
    # Print table labels
    print_labels(dataset)
    
    # Iterate over tables and measure disk usage
    disk_usages = []
    for N in N_values:
        index = create_index(dataset, N, conn=conn, cur=cur)
        execute_sql(f"SELECT pg_size_pretty(pg_total_relation_size('{index}'))", conn=conn, cur=cur)
        disk_usage = cur.fetchone()[0]
        disk_usages.append((N, disk_usage))
        print_row(N, disk_usage)
    
    # Close
    cur.close()
    conn.close()

    # Save data
    save_data(dataset, disk_usages)
  
def plot_data(dataset):
    data = fetch_data(dataset)
    N_values, disk_usages = zip(*data)
    x_values = list(map(convert_string_to_number, N_values))
    y_values = list(map(convert_bytes_to_number, disk_usages))
    
    fig = go.Figure(data=go.Scatter(x=x_values, y=y_values, mode='lines'))
    
    fig.update_layout(
        title=f"Disk Usage over Data Size for {dataset}",
        xaxis=dict(title='Data Size (bytes)'),
        yaxis=dict(title='Disk Usage (MB)'),
    )
    
    fig.show()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise Exception('Usage: python disk_usage.py sift 10k,100k,1m')
    
    dataset = sys.argv[1]
    N_values = sys.argv[2].split(',')
    generate_data(dataset, N_values)