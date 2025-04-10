from dash import Input, Output, State, callback_context, ALL
from dash import html, dcc
from .data import series, series_x
from .config import SERIES_WINDOW_SIZE
from .utils import parse_and_interpolate_path
import dash
import plotly.graph_objs as go
import numpy as np
import json


# Assuming you have access to series and series_x
def register_callbacks(app):
    @app.callback(
        Output('series-selector-container', 'children'),
        Input('selected-series-store', 'data')
    )
    def update_series_preview_list(selected):
        children = []
        for i in range(len(series)):
            is_selected = str(i) in selected
            border_style = '3px solid #007BFF' if is_selected else '1px solid #ccc'

            children.append(html.Div([
                dcc.Graph(
                    id={'type': 'series-preview', 'index': i},
                    figure={
                        'data': [{
                            'x': series_x[::10],
                            'y': series[i][::10],
                            'mode': 'lines',
                            'line': {'width': 1}
                        }],
                        'layout': {
                            'height': 40,
                            'margin': dict(l=10, r=10, t=10, b=10),
                            'xaxis': {'visible': False},
                            'yaxis': {'visible': False},
                            'showlegend': False
                        }
                    },
                    config={'staticPlot': True,
                            'displayModeBar': False},
                    style={'cursor': 'pointer', 'height': '40px'}
                ),
                html.Div(f"Series {i}", style={'textAlign': 'center', 'fontSize': '12px'})
            ], id={'type': 'series-card', 'index': i}, n_clicks=0, style={
                'border': border_style,
                'borderRadius': '6px',
                'padding': '4px',
                'backgroundColor': '#fff'
            }))
        return children

    # Toggle selection on click
    @app.callback(
        Output('selected-series-store', 'data'),
        Input({'type': 'series-card', 'index': ALL}, 'n_clicks'),
        State('selected-series-store', 'data')
    )
    def toggle_selection(n_clicks_list, current_selected):
        ctx = callback_context
        if not ctx.triggered or all(n is None for n in n_clicks_list):
            return current_selected

        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        index = eval(triggered_id)['index']
        index_str = str(index)

        selected = set(current_selected)
        if index_str in selected:
            selected.remove(index_str)
        else:
            selected.add(index_str)
        return list(selected)

    # Update main plot
    @app.callback(
        Output("example-plot", "figure"),
        Input("selected-series-store", "data")
    )
    def update_main_plot(selected_indices):
        if not selected_indices:
            return {
                'data': [],
                'layout': {'title': 'No Series Selected'}
            }

        fig = go.Figure()
        for idx in selected_indices:
            i = int(idx)
            fig.add_trace(go.Scatter(x=series_x, y=series[i], mode='lines', name=f"Series {i}"))

        fig.update_layout(title="Selected Series", margin=dict(t=30))
        return fig

    @app.callback(
        Output("submit-sketch", "children"),
        Input("submit-sketch", "n_clicks"),
        State("sketch-shape-store", "data")
    )
    def submit_sketch(n_clicks, shapes):
        print("Submit button triggered")
        if not n_clicks:
            raise dash.exceptions.PreventUpdate

        print("Submitted shapes:", shapes)
        return f"Submitted ({len(shapes)} shape{'s' if len(shapes) != 1 else ''})"

    @app.callback(
        Output('sketch-shape-store', 'data'),
        Input('sketch-graph', 'relayoutData'),
        State('sketch-shape-store', 'data')
    )
    def update_sketch_store(relayout_data, current_data):
        print("Relayout triggered:", relayout_data)
        if not relayout_data:
            raise dash.exceptions.PreventUpdate

        updated_shapes = parse_and_interpolate_path(relayout_data["shapes"][0]["path"]) if "shapes" in relayout_data else []

        return updated_shapes