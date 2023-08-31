import plotly.graph_objects as go
from .constants import Extension
from .colors import get_transparent_color, get_color_from_extension


def plot_line(fig: go.Figure, extension: Extension, index_params, x_values, y_values, index=0):
    fig.add_trace(go.Scatter(
        x=x_values,
        y=y_values,
        marker=dict(color=get_color_from_extension(extension, index)),
        mode='lines+markers',
        name=f"{extension.value.upper()} - {index_params}",
        legendgroup=extension.value.upper(),
        legendgrouptitle={'text': extension.value.upper()}
    ))


def plot_line_with_stddev(fig: go.Figure, extension: Extension, index_params, x_values, y_means, y_stddevs, index=0):
    plot_line(fig, extension, index_params, x_values, y_means, index=index)

    fig.add_trace(go.Scatter(
        # x values for both the top and bottom bounds
        x=x_values + x_values[::-1],
        # upper bound followed by lower bound
        y=[
            t + (s or 0) for t, s in zip(y_means, y_stddevs)]
        + [t - (s or 0) for t, s in zip(y_means, y_stddevs)][::-1],
        fill='toself',
        fillcolor=get_transparent_color(
            get_color_from_extension(extension, index)),
        # make the line invisible
        line=dict(color='rgba(255,255,255,0)'),
        showlegend=False,
        legendgroup=extension.value.upper(),
    ))
