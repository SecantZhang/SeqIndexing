from dash.dependencies import Input, Output
from .data import series, series_x
import plotly.graph_objs as go
import numpy as np


# Assuming you have access to series and series_x
def register_callbacks(app):
    @app.callback(
        Output("example-plot", "figure"),
        Input("series-selector", "value")
    )

    def update_main_plot(selected_indices):
        if not selected_indices:
            return {
                'data': [],
                'layout': {'title': 'Example Plot'}
            }

        fig = go.Figure()
        for idx in selected_indices:
            i = int(idx)
            fig.add_trace(go.Scatter(x=series_x, y=series[i], mode='lines', name=f"Series {i}"))

        fig.update_layout(title="Selected Series", margin=dict(t=30))
        return fig