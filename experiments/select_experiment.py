import os
import re
import psycopg2
import plotly.graph_objects as go
from tempfile import NamedTemporaryFile
from scripts.delete_index import delete_index
from scripts.create_index import create_index
from scripts.script_utils import run_command, save_result, extract_connection_params, execute_sql, parse_args
from scripts.number_utils import convert_string_to_number
import math

db_connection_string = os.environ.get('DATABASE_URL')


def get_latency_metric(bulk=False):
    return 'select (latency ms)' if not bulk else 'select bulk (latency ms)'


def get_tps_metric(bulk=False):
    return 'select (tps)' if not bulk else 'select bulk (tps)'


def generate_performance_result(dataset, N, K, bulk):
    base_table_name = f"{dataset}_base{N}"
    query_table_name = f"{dataset}_query{N}"
    N_number = convert_string_to_number(N)
    if bulk:
        query = f"""
            SELECT
                q.id AS query_id,
                ARRAY_AGG(b.id) AS base_ids
            FROM (
                SELECT
                    *
                FROM
                    {query_table_name}
                ORDER BY
                    RANDOM()
                LIMIT
                    100
            ) q
            JOIN LATERAL (
                SELECT
                    id,
                    v
                FROM
                    {base_table_name}
                ORDER BY
                    q.v <-> v
                LIMIT
                    {K}
            ) b ON true
            GROUP BY
                q.id
        """
    else:
        query = f"""
            \set id random(1, {N_number})

            SELECT *
            FROM {base_table_name}
            ORDER BY v <-> (
                SELECT v
                FROM {query_table_name}
                WHERE id = :id
            )
            LIMIT {K};
        """
    with NamedTemporaryFile(mode="w", delete=False) as tmp_file:
        tmp_file.write(query)
        tmp_file_path = tmp_file.name

    host, port, user, password, database = extract_connection_params(
        db_connection_string)
    command = f'PGPASSWORD={password} pgbench -d {database} -U {user} -h {host} -p {port} -f {tmp_file_path} -c 8 -j 8 -t 15 -r'
    stdout, stderr = run_command(command)

    # Extract latency average using regular expression
    latency_average = None
    latency_average_match = re.search(
        r'latency average = (\d+\.\d+) ms', stdout)
    if latency_average_match:
        latency_average = float(latency_average_match.group(1))

    # Extract TPS (Transactions Per Second) using regular expression
    tps = None
    tps_match = re.search(r'tps = (\d+\.\d+)', stdout)
    if tps_match:
        tps = float(tps_match.group(1))

    shared_response = {
        'out': stdout,
        'err': stderr,
    }

    tps_response = {
        **shared_response,
        'metric_value': tps,
        'metric_type': get_tps_metric(bulk),
    }

    latency_response = {
        **shared_response,
        'metric_value': latency_average,
        'metric_type': get_latency_metric(bulk),
    }

    return tps_response, latency_response


def generate_recall_result(dataset, N, K):
    base_table_name = f"{dataset}_base{N}"
    truth_table_name = f"{dataset}_truth{N}"
    query_table_name = f"{dataset}_query{N}"

    query_ids = execute_sql(
        f"SELECT id FROM {query_table_name} LIMIT 100", select=True)

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
    recall_response = {
        'metric_type': 'recall',
        'metric_value': recall_at_k,
    }
    return recall_response


def generate_result(extension, dataset, N, K_values, index_params={}, bulk=False):
    conn = psycopg2.connect(db_connection_string)
    cur = conn.cursor()

    delete_index(dataset, N, conn=conn, cur=cur)
    create_index(extension, dataset, N,
                 index_params=index_params, conn=conn, cur=cur)

    print(
        f"dataset = {dataset}, extension = {extension}, N = {N}, index_params = {index_params}")
    print("K".ljust(10), "TPS".ljust(10), "Latency (ms)".ljust(15), 'Recall')
    print('-' * 48)

    for K in K_values:
        save_result_params = {
            'database': extension,
            'database_params': index_params,
            'dataset': dataset,
            'n': convert_string_to_number(N),
            'k': K,
            'conn': conn,
            'cur': cur,
        }

        tps_response, latency_response = generate_performance_result(
            dataset, N, K, bulk)
        recall_response = generate_recall_result(dataset, N, K)
        save_result(**save_result_params, **tps_response)
        save_result(**save_result_params, **latency_response)
        save_result(**save_result_params, **recall_response)

        print(
            f"{K}".ljust(10),
            "{:.2f}".format(tps_response['metric_value']).ljust(10),
            "{:.2f}".format(latency_response['metric_value']).ljust(15),
            "{:.2f}".format(recall_response['metric_value'])
        )

    print()

    if extension != 'none':
        delete_index(dataset, N, conn=conn, cur=cur)

    cur.close()
    conn.close()


def get_extension_hyperparameters(extension, N):
    hyperparameters = []
    if extension == 'pgvector':
        sqrt_N = int(math.sqrt(convert_string_to_number(N)))
        lists_options = list(
            map(lambda p: int(p * sqrt_N), [0.6, 0.8, 1.0, 1.2, 1.4]))
        probes_options = [1, 2, 4, 8, 16, 32]
        hyperparameters = [{'lists': l, 'probes': p}
                           for l in lists_options for p in probes_options]
    if extension == 'lantern':
        m_options = [2, 4, 8, 16, 32]
        ef_construction_options = [16]  # [16, 32, 64, 128, 256]
        ef_options = [10]  # [10, 20, 40, 80, 160]
        hyperparameters = [{'M': m, 'ef_construction': efc, 'ef': ef}
                           for m in m_options for efc in ef_construction_options for ef in ef_options]
    return hyperparameters


def run_hyperparameter_search(extension, dataset, N):
    hyperparameters = get_extension_hyperparameters(extension, N)
    for hyperparameter in hyperparameters:
        generate_result(
            extension, dataset, N, [5], index_params=hyperparameter)


def plot_hyperparameter_search(extensions, dataset, N, xaxis='recall', yaxis='select (latency ms)'):
    colors = ['blue', 'red', 'green', 'yellow', 'purple']

    fig = go.Figure()

    for idx, extension in enumerate(extensions):
        sql = """
            SELECT
                database_params,
                MAX(CASE WHEN metric_type = %s THEN metric_value ELSE NULL END),
                MAX(CASE WHEN metric_type = %s THEN metric_value ELSE NULL END)
            FROM
                experiment_results
            WHERE
                database = %s
                AND dataset = %s
                AND N = %s
                AND (
                    metric_type = %s
                    OR metric_type = %s
                )
            GROUP BY
                database_params
        """
        data = (xaxis, yaxis, extension, dataset,
                convert_string_to_number(N), xaxis, yaxis)
        results = execute_sql(sql, data, select=True)

        index_params, xaxis_data, yaxis_data = zip(*results)

        fig.add_trace(go.Scatter(
            x=xaxis_data,
            y=yaxis_data,
            mode='markers',
            marker=dict(
                size=8,
                color=colors[idx % len(colors)],
                opacity=0.8
            ),
            hovertext=index_params,
            hoverinfo="x+y+text",
            name=extension
        ))

    fig.update_layout(
        title=f"{yaxis} and {xaxis} for with {dataset} {N}",
        xaxis=dict(title=xaxis),
        yaxis=dict(title=yaxis),
        margin=dict(l=50, r=50, b=50, t=50),
        hovermode='closest'
    )

    fig.show()


if __name__ == '__main__':
    extension, index_params, dataset, N_values, K_values = parse_args(
        "select experiment", ['extension', 'N', 'K'])
    for N in N_values:
        generate_result(extension, dataset, N, K_values, index_params)
