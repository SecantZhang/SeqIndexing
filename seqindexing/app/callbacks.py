from dash import Input, Output, State, callback_context, ALL
from dash import html, dcc
from .data import series, series_x, generate_dummy_matches
from .config import SERIES_WINDOW_SIZE
from .utils import parse_and_interpolate_path
import dash
import plotly.graph_objs as go
import numpy as np
import uuid


def register_callbacks(app):
    @app.callback(
        Output('series-selector-container', 'children'),
        Input('selected-series-store', 'data'),
        Input('match-results-store', 'data'),
        Input('distance-threshold-store', 'data')
    )
    def update_series_preview_list(selected, match_data, threshold):
        children = []
        color_list = ['blue', 'red', 'green', 'orange', 'purple']
        x_max = max(series_x)

        for i in range(len(series)):
            is_selected = str(i) in selected
            border_style = '3px solid #007BFF' if is_selected else '1px solid #ccc'
            color = color_list[i % len(color_list)]

            intervals = [
                m for m in match_data.get(str(i), [])
                if m['score'] <= threshold
            ]
            shapes = [
                {
                    'type': 'rect',
                    'xref': 'x',
                    'yref': 'paper',
                    'x0': interval['start'],
                    'x1': min(interval['end'], x_max),
                    'y0': 0,
                    'y1': 1,
                    'fillcolor': color,
                    'opacity': 0.2,
                    'line': {'width': 0},
                    'layer': 'below'
                }
                for interval in intervals
            ]

            children.append(html.Div([
                dcc.Graph(
                    id={'type': 'series-preview', 'index': i},
                    figure={
                        'data': [{
                            'x': series_x[::10],
                            'y': series[i][::10],
                            'mode': 'lines',
                            'line': {'width': 1, 'color': color}
                        }],
                        'layout': {
                            'height': 40,
                            'margin': dict(l=10, r=10, t=10, b=10),
                            'xaxis': {'visible': False},
                            'yaxis': {'visible': False},
                            'showlegend': False,
                            'shapes': shapes
                        }
                    },
                    config={'staticPlot': True, 'displayModeBar': False},
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

    @app.callback(
        Output('selected-series-store', 'data'),
        Input({'type': 'series-card', 'index': ALL}, 'n_clicks'),
        State('selected-series-store', 'data')
    )
    def toggle_selection(n_clicks_list, current_selected):
        print(f"toggle selection callback triggered, n_clicks_list={n_clicks_list}, current_selected={current_selected}")
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

    @app.callback(
        Output("example-plot", "figure"),
        Input("selected-series-store", "data"),
        Input('distance-threshold-store', 'data'),
        State("match-results-store", "data")
    )
    def update_main_plot(selected_indices, threshold, match_data):
        if not selected_indices:
            return {
                'data': [],
                'layout': {'title': 'No Series Selected'}
            }

        fig = go.Figure()
        color_list = ['blue', 'red', 'green', 'orange', 'purple']
        x_max = max(series_x)

        for idx_num, idx in enumerate(selected_indices):
            i = int(idx)
            color = color_list[i % len(color_list)]

            fig.add_trace(go.Scatter(
                x=series_x,
                y=series[i],
                mode='lines',
                name=f"Series {i}",
                line={'color': color}
            ))

            intervals = [
                m for m in match_data.get(str(i), [])
                if m['score'] <= threshold
            ]
            for j, interval in enumerate(intervals, start=1):
                fig.add_vrect(
                    x0=interval['start'],
                    x1=min(interval['end'], x_max),
                    fillcolor=color,
                    opacity=0.2,
                    layer='below',
                    line_width=0,
                    annotation_text=f"Series {i} Match {j}",
                    annotation_position='top left'
                )

        # Enable a numeric range slider.
        fig.update_layout(
            title="Selected Series with Highlighted Matches",
            margin=dict(t=30),
            xaxis=dict(
                rangeslider=dict(
                    visible=True
                ),
                # If your x-axis is time-based, set 'type': 'date' and add 'rangeselector'
                # If numeric, just keep 'type': 'linear'.
                type='linear'
            )
        )

        return fig

    @app.callback(
        Output("submit-sketch", "children"),
        Output("match-results-store", "data"),
        Output("distance-histogram", "figure"),
        Output("distance-threshold-slider", "max"),
        Output("distance-threshold-slider", "value"),
        Output("sketch-history-store", "data"),
        Output("active-sketch-id", "data"),
        Input("submit-sketch", "n_clicks"),
        State("sketch-shape-store", "data"),
        State("sketch-history-store", "data")
    )
    def submit_sketch(n_clicks, shapes, history):
        print(f"submit sketch triggered, n_clicks={n_clicks}, shapes={shapes}")
        if not n_clicks or not shapes:
            raise dash.exceptions.PreventUpdate

        sketch_id = str(uuid.uuid4())
        history = history if len(history) != 0 else {}
        history[sketch_id] = shapes

        print(f"current history - {len(history)}: {history}")

        sketch = np.array(shapes)
        topk_matches = generate_dummy_matches(series)

        # Flatten all distances
        all_scores = [score for row in topk_matches for (_, _, score) in row]
        max_dist = max(all_scores) if all_scores else 1.0

        # Format results
        formatted = {
            str(i): [{"start": series_x[start], "end": series_x[min(end, len(series_x) - 1)], "score": float(score)}
                     for start, end, score in matches]
            for i, matches in enumerate(topk_matches)
        }

        # Histogram
        hist_fig = go.Figure()
        hist_fig.add_trace(go.Histogram(
            x=all_scores,
            nbinsx=30,
            marker_color="rgba(33, 150, 243, 0.4)",  # blue
            marker_line_color="rgba(33, 150, 243, 1)",
            marker_line_width=1,
            opacity=0.85
        ))
        hist_fig.update_layout(
            margin=dict(t=8, b=8, l=8, r=8),
            height=90,
            bargap=0.2,
            # xaxis=dict(
            #     title="Distance",
            #     title_font=dict(size=11, color='#333'),
            #     tickfont=dict(size=9),
            #     zeroline=False,
            #     showgrid=False
            # ),
            # yaxis=dict(
            #     title="Count",
            #     title_font=dict(size=11, color='#333'),
            #     tickfont=dict(size=9),
            #     zeroline=False,
            #     showgrid=False
            # ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )

        return (
            f"Submitted ({len(shapes)} shape{'s' if len(shapes) != 1 else ''})",
            formatted,
            hist_fig,
            max_dist,
            max_dist,
            history,
            sketch_id
        )

    @app.callback(
        Output('sketch-shape-store', 'data'),
        Input('sketch-graph', 'relayoutData'),
        State('sketch-shape-store', 'data')
    )
    def update_sketch_store(relayout_data, current_data):
        if not relayout_data:
            raise dash.exceptions.PreventUpdate

        updated_shapes = parse_and_interpolate_path(relayout_data["shapes"][0]["path"]) if "shapes" in relayout_data else []
        return updated_shapes

    @app.callback(
        Output("distance-threshold-store", "data"),
        Input("distance-threshold-slider", "value")
    )
    def update_threshold_store(value):
        return value

    @app.callback(
        Output("sketch-graph-container", "children"),
        Input("sketch-refresh-key", "data"),
    )
    def render_sketch_graph(refresh_key):
        print("sketch area rendered with refresh key {}".format(refresh_key))
        return html.Div([
            dcc.Graph(
                id='sketch-graph',
                config={
                    'modeBarButtonsToAdd': [
                        'drawline', 'drawopenpath', 'drawclosedpath',
                        'drawcircle', 'drawrect', 'eraseshape'
                    ],
                    'editable': True,
                    'scrollZoom': True
                },
                figure={
                    'layout': {
                        'dragmode': 'drawopenpath',
                        'newshape': {
                            'line': {'color': 'red'},
                            'fillcolor': 'rgba(0,0,0,0)',
                            'opacity': 0.5
                        },
                        'margin': {'l': 0, 'r': 0, 't': 0, 'b': 0},
                        'xaxis': {'visible': False},
                        'yaxis': {'visible': False},
                        'shapes': []
                    }
                },
                style={
                    'height': '400px',
                    'border': '1px solid #ccc'
                }
            )
        ], key=str(refresh_key))

    @app.callback(
        Output("sketch-refresh-key", "data"),
        Input("refresh-sketch", "n_clicks"),
        State("sketch-refresh-key", "data"),
        prevent_initial_call=True
    )
    def refresh_sketch_view(n_clicks, current_key):
        print(f"sketch area refreshed, current key: {current_key}")
        return current_key + 1  # just bump the key to remount the component

    @app.callback(
        Output("sketch-history-list", "children"),
        Input("sketch-history-store", "data")
    )
    def render_sketch_history(history):
        if not history:
            return []

        preview_components = []
        for sketch_id, y_values in history.items():
            preview_fig = {
                'data': [{
                    'x': list(range(len(y_values))),
                    'y': y_values,
                    'mode': 'lines',
                    'line': {'width': 1, 'color': '#444'}
                }],
                'layout': {
                    'height': 40,
                    'margin': {'l': 0, 'r': 0, 't': 0, 'b': 0},
                    'xaxis': {'visible': False},
                    'yaxis': {'visible': False},
                    'showlegend': False,
                    'dragmode': False,
                    'hovermode': False
                }
            }

            preview_components.append(html.Div([
                dcc.Graph(
                    figure=preview_fig,
                    config={'staticPlot': True, 'displayModeBar': False},
                    style={'height': '40px', 'width': '80px'}
                )
            ], id={'type': 'history-card', 'index': sketch_id},
                n_clicks=0,
                style={
                    'border': '1px solid #ccc',
                    'borderRadius': '4px',
                    'padding': '2px',
                    'cursor': 'pointer'
                }))

        return preview_components