import os
import re
import psycopg2
import plotly.graph_objects as go
from tempfile import NamedTemporaryFile
from scripts.delete_index import delete_index
from scripts.create_index import create_index
from scripts.script_utils import get_table_name, run_command, save_result, extract_connection_params, VALID_DATASETS, SUGGESTED_K_VALUES, execute_sql, VALID_EXTENSIONS_AND_NONE, parse_args
from utils.colors import get_color_from_extension
from scripts.number_utils import convert_string_to_number


def get_latency_metric(bulk=False):
    return 'select (latency ms)' if not bulk else 'select bulk (latency ms)'


def get_tps_metric(bulk=False):
    return 'select (tps)' if not bulk else 'select bulk (tps)'


def generate_result(extension, dataset, N, K_values, index_params={}, bulk=False):
    db_connection_string = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(db_connection_string)
    cur = conn.cursor()

    delete_index(dataset, N, conn=conn, cur=cur)
    create_index(extension, dataset, N,
                 index_params=index_params, conn=conn, cur=cur)

    print(
        f"dataset = {dataset}, extension = {extension}, N = {N}, index_params = {index_params}")
    print("K".ljust(10), "TPS".ljust(10), "Latency (ms)".ljust(12))
    print('-' * 32)

    base_table_name = f"{dataset}_base{N}"
    query_table_name = f"{dataset}_query{N}"
    N_number = convert_string_to_number(N)

    for K in K_values:
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

        save_result_params = {
            'database': extension,
            'database_params': index_params,
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
        latency_average_match = re.search(
            r'latency average = (\d+\.\d+) ms', stdout)
        if latency_average_match:
            latency_average = float(latency_average_match.group(1))
            save_result(
                metric_type='select (latency ms)',
                metric_value=latency_average,
                **save_result_params
            )

        # Extract TPS (Transactions Per Second) using regular expression
        tps = None
        tps_match = re.search(r'tps = (\d+\.\d+)', stdout)
        if tps_match:
            tps = float(tps_match.group(1))
            save_result(
                metric_type='select (tps)',
                metric_value=tps,
                **save_result_params
            )

        print(f"{K}".ljust(10), "{:.2f}".format(tps).ljust(
            10), "{:.2f}".format(latency_average))

    print()

    if extension != 'none':
        delete_index(dataset, N, conn=conn, cur=cur)

    cur.close()
    conn.close()


full_strings = {
    'N': 'Number of rows (N)',
    'K': 'Number of similar vectors (K)'
}


def plot_result(metric_type, dataset, x_params, x, y, fixed, fixed_value):
    fig = go.Figure()
    for extension in VALID_EXTENSIONS_AND_NONE:
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
            fig.add_trace(go.Scatter(
                x=x_values,
                y=y_values,
                marker=dict(color=color),
                mode='lines+markers',
                name=extension
            ))
    fig.update_layout(
        title=f"{y} vs. {x}",
        xaxis_title=full_strings[x],
        yaxis_title=y
    )
    fig.show()


def plot_results(dataset, bulk=False):
    N_values = list(map(convert_string_to_number, VALID_DATASETS[dataset]))
    plot_result(metric_type=get_latency_metric(bulk), dataset=dataset,
                x_params=N_values, x='N', y='latency (ms)', fixed='K', fixed_value=5)
    plot_result(metric_type=get_latency_metric(bulk), dataset=dataset,
                x_params=SUGGESTED_K_VALUES, x='K', y='latency (ms)', fixed='N', fixed_value=100000)
    plot_result(metric_type=get_tps_metric(bulk), dataset=dataset, x_params=N_values,
                x='N', y='transactions / second', fixed='K', fixed_value=5)
    plot_result(metric_type=get_tps_metric(bulk), dataset=dataset, x_params=SUGGESTED_K_VALUES,
                x='K', y='transactions / second', fixed='N', fixed_value=100000)


if __name__ == '__main__':
    extension, index_params, dataset, N_values, K_values = parse_args(
        "select experiment", ['extension', 'N', 'K'])
    for N in N_values:
        generate_result(extension, dataset, N, K_values, index_params)
