import plotly.graph_objects as go
from core.utils.constants import Metric
from core.utils.database import DatabaseConnection
from core.utils.numbers import convert_string_to_number
from core.hyperparameter_search import HYPERPARAMETER_SEARCH_K


def plot_hyperparameter_search(extensions, dataset, N, xaxis=Metric.RECALL, yaxis=Metric.SELECT_LATENCY):
    colors = ['blue', 'orange', 'green', 'purple', 'red']

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
                AND K = %s
                AND metric_type = ANY(%s)
            GROUP BY
                index_params
        """
        data = (xaxis.value, yaxis.value, extension.value, dataset.value,
                convert_string_to_number(N), HYPERPARAMETER_SEARCH_K, [xaxis.value, yaxis.value])
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
