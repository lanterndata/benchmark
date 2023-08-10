
import math
import recall_experiment
import select_experiment
from scripts.script_utils import convert_string_to_number, execute_sql
import plotly.graph_objects as go


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
        m_options = [2, 3, 4, 6, 8, 16, 24, 32]
        ef_construction_options = [16]  # [16, 32, 64, 128, 256]
        ef_options = [10]  # [10, 20, 40, 80, 160]
        hyperparameters = [{'M': m, 'ef_construction': efc, 'ef': ef}
                           for m in m_options for efc in ef_construction_options for ef in ef_options]
    return hyperparameters


def run_hyperparameter_search(extension, dataset, N):
    hyperparameters = get_extension_hyperparameters(extension, N)
    for hyperparameter in hyperparameters:
        recall_experiment.generate_result(
            extension, dataset, N, [5], index_params=hyperparameter)
        select_experiment.generate_result(
            extension, dataset, N, [5], index_params=hyperparameter)


def plot_hyperparameter_search(extension, dataset, N, metric1='recall', metric2='select (latency ms)'):
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
    data = (metric1, metric2, extension, dataset,
            convert_string_to_number(N), metric1, metric2)
    results = execute_sql(sql, data, select=True)

    index_params, metrics1, metrics2 = zip(*results)

    # Create a scatter plot
    fig = go.Figure(data=go.Scatter(
        x=metrics1,
        y=metrics2,
        mode='markers',
        marker=dict(
            size=10,
            color='blue',
            opacity=0.8
        ),
        hovertext=index_params,
        hoverinfo="x+y+text"
    ))

    # Set the layout properties
    fig.update_layout(
        title=f"Tradeoffs between {metric2} and {metric1} for {extension} with {dataset} {N}",
        xaxis=dict(title=metric1),
        yaxis=dict(title=metric2),
        margin=dict(l=50, r=50, b=50, t=50),
        hovermode='closest'
    )

    # Display the plot
    fig.show()


def choose_hyperparameters(extension, dataset, N):
    return
