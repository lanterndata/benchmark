import plotly.graph_objects as go
from utils.constants import Metric, Extension
from utils.database import DatabaseConnection
from utils.numbers import convert_string_to_number
from .select_experiment import generate_result
import math

HYPERPARAMETER_SEARCH_K = 5


def get_extension_hyperparameters(extension, N):
    hyperparameters = []
    if extension == Extension.PGVECTOR:
        sqrt_N = int(math.sqrt(convert_string_to_number(N)))
        lists_options = list(
            map(lambda p: int(p * sqrt_N), [0.6, 0.8, 1.0, 1.2, 1.4]))
        probes_options = [1, 2, 4, 8, 16, 32]
        hyperparameters = [{'lists': l, 'probes': p}
                           for l in lists_options for p in probes_options]
    if extension == Extension.LANTERN or extension == Extension.NEON:
        m_options = [2, 4, 6, 8, 12, 16, 24, 32, 48, 64]
        ef_construction_options = [16]  # [16, 32, 64, 128, 256]
        ef_options = [10]  # [10, 20, 40, 80, 160]
        hyperparameters = [{'M': m, 'ef_construction': efc, 'ef': ef}
                           for m in m_options for efc in ef_construction_options for ef in ef_options]
    if extension == Extension.NONE:
        return [{}]
    return hyperparameters


def run_hyperparameter_search(extension, dataset, N, bulk=False):
    hyperparameters = get_extension_hyperparameters(extension, N)
    for hyperparameter in hyperparameters:
        generate_result(
            extension, dataset, N, [HYPERPARAMETER_SEARCH_K], index_params=hyperparameter, bulk=bulk)


def plot_hyperparameter_search(extensions, dataset, N, xaxis=Metric.RECALL, yaxis=Metric.SELECT_LATENCY):
    colors = ['blue', 'red', 'green', 'purple']

    fig = go.Figure()

    for idx, extension in enumerate(extensions):
        sql = """
            SELECT
                index_params,
                MAX(CASE WHEN metric_type = %s THEN metric_value ELSE NULL END),
                MAX(CASE WHEN metric_type = %s THEN metric_value ELSE NULL END)
            FROM
                experiment_results
            WHERE
                extension = %s
                AND dataset = %s
                AND N = %s
                AND K = {HYPERPARAMETER_SEARCH_K}
                AND metric_type = ANY(%s)
            GROUP BY
                index_params
        """
        data = (xaxis.value, yaxis.value, extension.value, dataset.value,
                convert_string_to_number(N), [xaxis.value, yaxis.value])
        with DatabaseConnection() as conn:
            results = conn.select(sql, data=data)

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
            name=extension.value.upper()
        ))

    fig.update_layout(
        title=f"{yaxis.value} and {xaxis.value} for with {dataset.value} {N}",
        xaxis=dict(title=xaxis.value),
        yaxis=dict(title=yaxis.value),
        margin=dict(l=50, r=50, b=50, t=50),
        hovermode='closest'
    )

    fig.show()
