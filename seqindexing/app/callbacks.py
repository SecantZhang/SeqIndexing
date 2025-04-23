from dash import Input, Output, State, callback_context, ALL
from dash import html, dcc
from .data import series, query_chroma_topk, generate_dummy_matches
from .config import SERIES_WINDOW_SIZE
from .utils import parse_and_interpolate_path, get_color_palette
import dash
import plotly.graph_objs as go
import numpy as np
import uuid


def register_callbacks(app):
    @app.callback(
        Output('series-selector-container', 'children'),
        Input('selected-series-store', 'data'),
        Input('match-results-store', 'data'),
        Input('distance-threshold-store', 'data'),
        Input('series-name-filter', 'value'),
        Input('window-size-slider', 'value')  # ✅ NEW
    )
    def update_series_preview_list(selected, match_data, threshold, filtered_names, window_size_range):
        children = []
        color_list = get_color_palette(series["shape"][0])
        x_max = max(series["x"])
        titles = series["titles"]
        name_to_index = {name: i for i, name in enumerate(titles)}

        # Decide which names to show
        if not match_data:
            sorted_names = sorted(titles)[:10]
        else:
            match_counts = {
                name: sum(
                    1 for matches in match_data[name].values()
                    for m in matches if m['score'] <= threshold
                )
                for name in match_data
            }
            filtered = {n: c for n, c in match_counts.items() if c > 0}
            sorted_names = sorted(filtered, key=lambda n: -filtered[n])

        for name in sorted_names:
            if filtered_names and name not in filtered_names:
                continue

            i = name_to_index[name]
            is_selected = str(i) in selected
            # grey border vs blue border
            border_style = '3px solid #007BFF' if is_selected else '1px solid #ccc'
            # grey line vs series color
            preview_color = color_list[i % len(color_list)] if is_selected else '#ccc'

            # only show shading in the mini‐chart if that card is selected
            shapes = []
            if match_data and name in match_data:
                min_ws, max_ws = window_size_range
                pattern_intervals = {
                    pattern_id: [
                        match for match in matches
                        if match["score"] <= threshold and min_ws <= match["window_size"] <= max_ws
                    ]
                    for pattern_id, matches in match_data[name].items()
                }
                for p_idx, (pattern_id, matches) in enumerate(pattern_intervals.items()):
                    for match in matches:
                        shapes.append({
                            'type': 'rect',
                            'xref': 'x',
                            'yref': 'paper',
                            'x0': series["x"][match['start_idx']],
                            'x1': min(series["x"][match['end_idx']], x_max),
                            'y0': 0,
                            'y1': 1,
                            'fillcolor': color_list[p_idx % len(color_list)],
                            'opacity': 0.25,
                            'line': {
                                'width': 1,
                                'color': color_list[p_idx % len(color_list)],
                                'dash': ['solid', 'dot', 'dash', 'longdash'][p_idx % 4]  # <-- DASH STYLE
                            },
                            'layer': 'below'
                        })

            children.append(html.Div([
                dcc.Graph(
                    id={'type': 'series-preview', 'index': i},
                    figure={
                        'data': [{
                            'x': series["x"][::10],
                            'y': series["y"][i][::10],
                            'mode': 'lines',
                            'line': {'width': 1, 'color': preview_color}
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
                html.Div(name, style={'textAlign': 'center', 'fontSize': '12px'})
            ],
                id={'type': 'series-card', 'index': i},
                n_clicks=0,
                style={
                    'border': border_style,
                    'borderRadius': '6px',
                    'padding': '4px',
                    'backgroundColor': '#fff',
                    # you can add 'width':'100%' here if needed in layout
                }
            ))

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
        idx = eval(triggered_id)['index']
        sel = set(current_selected)
        if str(idx) in sel:
            sel.remove(str(idx))
        else:
            sel.add(str(idx))
        return list(sel)


    @app.callback(
        Output("example-plot", "figure"),
        Input("selected-series-store", "data"),
        Input("distance-threshold-store", "data"),
        Input("window-size-slider", "value"),
        State("match-results-store", "data")
    )
    def update_main_plot(selected_indices, threshold, window_size_range, match_data):
        if not selected_indices:
            return {'data': [], 'layout': {'title': 'No Series Selected'}}

        fig = go.Figure()
        color_list = get_color_palette(series["shape"][0])
        x_max = max(series["x"])
        titles = series["titles"]
        min_ws, max_ws = window_size_range

        for idx in selected_indices:
            i = int(idx)
            name = titles[i]
            color = color_list[i % len(color_list)]

            # Draw the main series line
            fig.add_trace(go.Scatter(
                x=series["x"],
                y=series["y"][i],
                mode='lines',
                name=name,
                line={'color': color}
            ))

            if match_data and name in match_data:
                for p_idx, (pattern_id, matches) in enumerate(match_data[name].items()):
                    filtered_matches = [
                        m for m in matches
                        if m["score"] <= threshold and min_ws <= m["window_size"] <= max_ws
                    ]
                    for j, interval in enumerate(filtered_matches, start=1):
                        fig.add_vrect(
                            x0=series["x"][interval["start_idx"]],
                            x1=min(series["x"][interval["end_idx"]], x_max),
                            fillcolor=color,
                            opacity=0.25,
                            layer='below',
                            line_width=1,
                            line_dash=['solid', 'dot', 'dash', 'longdash'][p_idx % 4],  # 🎨 dash by pattern
                            annotation_text=f"Match {j}",
                            annotation_position='top left'
                        )

        fig.update_layout(
            title="Selected Series with Highlighted Matches",
            height=500,  # make it taller
            margin=dict(t=25, l=10, r=10, b=10),
            legend=dict(
                x=1.02, y=1,
                xanchor='left',
                yanchor='top'
            ),
            xaxis=dict(
                rangeslider=dict(visible=True),
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
        Output("auto-select-series", "data"),  # ✅ new output
        Input("submit-sketch", "n_clicks"),
        State("sketch-shape-store", "data"),
        State("sketch-history-store", "data"),
        State("window-size-store", "data"),
        prevent_initial_call=True
    )
    def submit_sketch(n_clicks, shapes, history, window_size):
        if not n_clicks or not shapes:
            raise dash.exceptions.PreventUpdate

        sketch_id = str(uuid.uuid4())
        history = history or {}
        history[sketch_id] = shapes
        print(history)
        name_to_index = {name: i for i, name in enumerate(series["titles"])}

        sketch = np.array(shapes)
        # topk_matches = generate_dummy_matches(history)
        topk_matches = query_chroma_topk(history)

        all_scores = [match["score"] for matches in topk_matches.values() for match in matches]
        max_dist = max(all_scores) if all_scores else 1.0

        reformatted = {}

        for curr_uuid, matches in topk_matches.items():
            for match in matches:
                name = match["name"]
                entry = {
                    "start_idx": match["start_idx"],
                    "end_idx": match["end_idx"],
                    "score": match["score"],
                    "window_size": match["end_idx"] - match["start_idx"]
                }

                # Initialize levels as needed
                if name not in reformatted:
                    reformatted[name] = {}
                if curr_uuid not in reformatted[name]:
                    reformatted[name][curr_uuid] = []

                reformatted[name][curr_uuid].append(entry)

        hist_fig = go.Figure()
        hist_fig.add_trace(go.Histogram(
            x=all_scores,
            nbinsx=30,
            marker_color="rgba(33, 150, 243, 0.4)",
            marker_line_color="rgba(33, 150, 243, 1)",
            marker_line_width=1,
            opacity=0.85
        ))
        hist_fig.update_layout(
            margin=dict(t=8, b=8, l=8, r=8),
            height=90,
            bargap=0.2,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )

        matched_indices = set()

        for name, uuid_dict in reformatted.items():
            idx = name_to_index.get(name)
            if idx is not None:
                matched_indices.add(str(idx))

        matched_series = list(matched_indices)
        print(f"current window_size = {window_size}")

        return (
            f"Submitted ({len(shapes)} shape{'s' if len(shapes) != 1 else ''})",
            reformatted,
            hist_fig,
            max_dist,
            max_dist,
            history,
            sketch_id,
            matched_series  # send to auto-select
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

    @app.callback(
        Output("window-size-store", "data"),
        Input("window-size-slider", "value")
    )
    def update_window_size(val):
        print(f"slider updated with value = {val}")
        return val

    @app.callback(
        Output("window-size-slider", "min"),
        Output("window-size-slider", "max"),
        Output("window-size-slider", "marks"),
        Output("window-size-slider", "value"),
        Input("match-results-store", "data")
    )
    def update_window_size_slider(match_data):
        default_marks = {7: "7", 15: "15", 30: "30"}
        default_range = [7, 30]

        if not match_data:
            return 7, 30, default_marks, default_range

        # Extract unique window sizes
        window_sizes = {
            match["window_size"]
            for matches_by_uuid in match_data.values()
            for matches in matches_by_uuid.values()
            for match in matches
        }

        if not window_sizes:
            return 7, 30, default_marks, default_range

        sorted_sizes = sorted(window_sizes)
        marks = {size: str(size) for size in sorted_sizes}
        min_val = sorted_sizes[0]
        max_val = sorted_sizes[-1]
        default_val = [min_val, max_val]

        return min_val, max_val, marks, [min_val, max_val]