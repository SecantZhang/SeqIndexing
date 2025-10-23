from dash import Input, Output, State, callback_context, ALL
from dash import html, dcc
from .data import series, query_chroma_topk_for_each_name
from .config import SERIES_WINDOW_SIZE
from .utils import parse_and_interpolate_path, get_color_palette
import dash
import plotly.graph_objs as go
import numpy as np
import uuid
import copy
try:
    from seqindexing.data.data_sp500 import (
        WINDOW_SIZES,
        WINDOW_UNIT,
        WINDOW_PRESETS,
        WINDOW_SIZE_LABELS,
    )
except Exception:
    from ..data.data_sp500 import (
        WINDOW_SIZES,
        WINDOW_UNIT,
        WINDOW_PRESETS,
        WINDOW_SIZE_LABELS,
    )


def register_callbacks(app):
    @app.callback(
        Output('series-selector-container', 'children'),
        Input('selected-series-store', 'data'),
        Input('match-results-store', 'data'),
        Input('distance-threshold-store', 'data'),
        Input('series-name-filter', 'value'),
        Input("window-size-min-input", "value"),
        Input("window-size-max-input", "value"),
        State("series-to-sketch-map", "data"),
        State("sketch-color-list", "data"),
        Input("active-patterns-with-selection", "data"),
        Input("active-sketch-id", "data")
    )
    def update_series_preview_list(selected, match_data, threshold, filtered_names, min_ws, max_ws, series_to_sketch, color_list, patterns_history_with_selection, active_sketch_id):
        print(f"update_series_preview_list triggered with selected={selected}, threshold={threshold}, filtered_names={filtered_names}, min_ws={min_ws}, max_ws={max_ws}")
        children = []
        x_max = max(series["x"])
        titles = series["titles"]
        name_to_index = {name: i for i, name in enumerate(titles)}

        # Decide which names to show
        if not match_data:
            sorted_names = sorted(titles)[:20]
        else:
            match_counts = {
                name: sum(
                    1 for matches in match_data[name].values()
                    for m in matches if m.get('score') is not None and m['score'] <= threshold
                )
                for name in match_data
            }
            filtered = {n: c for n, c in match_counts.items() if c > 0}
            sorted_names = sorted(filtered, key=lambda n: -filtered[n])

        selected = selected or []
        prev_selected_series = [v["selected_series"] for k, v in patterns_history_with_selection.items() if v.get("selected_series") is not None][:-1]
        print(f"prev_selected_series = {prev_selected_series}")
        prev_patterns = list(patterns_history_with_selection.keys())

        for name in sorted_names:
            if filtered_names and name not in filtered_names:
                continue

            i = name_to_index[name]
            is_selected = str(i) in selected
            border_style = '3px solid #007BFF' if is_selected else '0px solid #ccc'
            sketch_idx = series_to_sketch.get(str(i), i)
            preview_color = color_list[sketch_idx % len(color_list)] if is_selected else '#ccc'

            # only show shading in the mini‐chart if that card is selected
            shapes = []
            if match_data and name in match_data:
                pattern_intervals = {
                    pattern_id: [
                        match for match in matches
                        if match["score"] <= threshold and min_ws <= match["window_size"] <= max_ws
                    ]
                    for pattern_id, matches in match_data[name].items()
                }
                for p_idx, (pattern_id, matches) in enumerate(pattern_intervals.items()):
                    if (patterns_history_with_selection == {} or  # case 1: initial preview generation
                            pattern_id == active_sketch_id or  # case 2: current
                            (pattern_id in prev_patterns and str(name_to_index[name]) in prev_selected_series)):
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
                                    'dash': ['solid', 'dot', 'dash', 'longdash'][p_idx % 4]
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
                }
            ))

        return children

    @app.callback(
        Output('selected-series-store', 'data'),
        Output("active-patterns-with-selection", "data"),
        Input({'type': 'series-card', 'index': ALL}, 'n_clicks'),
        State('selected-series-store', 'data'),
        State('series-to-sketch-map', 'data'),
        State("active-patterns", "data"),
        Input("active-patterns-with-selection", "data"), 
        State('active-sketch-id', 'data'),
    )
    def toggle_selection(n_clicks_list, current_selected, series_to_sketch, active_patterns, active_patterns_with_selection, active_sketch_id):
        print(f"toggle_selection triggered")
        ctx = callback_context
        if not ctx.triggered or all(n == 0 or n is None for n in n_clicks_list):
            return current_selected or [], dash.no_update

        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        idx = str(eval(triggered_id)['index'])
        
        print(triggered_id)
        print(idx)

        # Find the pattern/sketch this series belongs to
        pattern_idx = str(series_to_sketch.get(idx))
        if pattern_idx is None:
            return current_selected or [], dash.no_update

        # Remove any other selected series from the same pattern
        new_selected = []
        for sel_idx in (current_selected or []):
            if series_to_sketch.get(sel_idx) != series_to_sketch.get(idx):
                new_selected.append(sel_idx)

        # Toggle: add if not present, remove if present
        if idx not in new_selected:
            new_selected.append(idx)
        print(active_sketch_id)
        print(len(active_patterns))

        if active_patterns_with_selection == {}:
            active_patterns_with_selection = copy.deepcopy(active_patterns)
        else:
            for pattern_uuid, pattern in active_patterns.items():
                if pattern_uuid not in active_patterns_with_selection:
                    active_patterns_with_selection[pattern_uuid] = active_patterns[pattern_uuid]

        # If there's no active sketch yet, don't try to attach selection
        if not active_sketch_id:
            return new_selected, dash.no_update

        key = str(active_sketch_id)

        # Ensure the active sketch exists in the selection mapping
        if key not in active_patterns_with_selection:
            if active_patterns and key in active_patterns:
                active_patterns_with_selection[key] = active_patterns[key]
            else:
                # Nothing to attach to; just update selection store
                return new_selected, dash.no_update

        # Now you can safely assign
        active_patterns_with_selection[key]["selected_series"] = idx
        active_patterns_with_selection[key]["selected_series_name"] = series["titles"][int(idx)]
        

        print(len(active_patterns_with_selection))

        return new_selected, active_patterns_with_selection
    
    @app.callback(
        Output("example-plot", "figure"),
        Input("active-patterns-with-selection", "data"),
        Input('selected-series-store', 'data'),
        State("distance-threshold-store", "data"),
        Input("window-size-min-input", "value"),
        Input("window-size-max-input", "value"),
    )
    def update_main_plot(active_patterns, selected, threshold, min_ws, max_ws):
        print(f"update_main_plot triggered")
        fig = go.Figure()
        xaxis_style = dict(
            rangeslider=dict(visible=True, thickness=0.07, bgcolor="#f5f5f5"),
            type='date',
            showgrid=True,
            gridcolor='#eeeeee',
            zeroline=False,
            linecolor='#bdbdbd',
            linewidth=1,
            tickfont=dict(family="Roboto, Arial, sans-serif", size=13, color="#616161"),
            title_font=dict(family="Roboto, Arial, sans-serif", size=15, color="#757575"),
        )
        yaxis_style = dict(
            showgrid=True,
            gridcolor='#eeeeee',
            zeroline=False,
            linecolor='#bdbdbd',
            linewidth=1,
            tickfont=dict(family="Roboto, Arial, sans-serif", size=13, color="#616161"),
            title_font=dict(family="Roboto, Arial, sans-serif", size=15, color="#757575"),
            title=dict(
                text="Dollar ($)",
                standoff=12,
                font=dict(family="Roboto, Arial, sans-serif", size=15, color="#757575"),
            ),
        )
        layout_style = dict(
            # title="Active Patterns and Their Matches",
            title_font=dict(family="Roboto, Arial, sans-serif", size=22, color="#212121"),
            # height=500,
            margin=dict(t=32, l=24, r=24, b=24),
            legend=dict(
                x=1.02, y=1,
                xanchor='left',
                yanchor='top',
                bgcolor='rgba(255,255,255,0.95)',
                bordercolor='#e0e0e0',
                borderwidth=1,
                font=dict(family="Roboto, Arial, sans-serif", size=13, color="#424242")
            ),
            xaxis=xaxis_style,
            yaxis=yaxis_style,
            plot_bgcolor='#fff',
            paper_bgcolor='#fff',
            font=dict(family="Roboto, Arial, sans-serif", color="#212121"),
            hoverlabel=dict(
                bgcolor="#fafafa",
                font_size=13,
                font_family="Roboto, Arial, sans-serif"
            )
        )

        # Fallback: if no active patterns yet, render any explicitly selected series
        if not active_patterns:
            selected = list(selected or [])
            if selected:
                for idx in selected[:1]:  # show the first selection to keep the view clean
                    i = int(idx)
                    fig.add_trace(go.Scatter(
                        x=series["x_date"],
                        y=series["y"][i],
                        mode='lines',
                        name=series["titles"][i],
                        line={'color': '#2196f3'}
                    ))
            fig.update_layout(**layout_style)
            return fig

        x_max = max(series["x"])
        titles = series["titles"]
        selected = set(selected or [])

        for pattern_id, pattern_info in active_patterns.items():
            color = pattern_info["color"]
            matched_patterns = pattern_info["matched_patterns"]
            # Determine which series index to plot
            i_val = pattern_info.get("selected_series")
            if i_val is None:
                # Fallback to the first selection, if available
                if selected:
                    i_val = int(list(selected)[0])
                else:
                    continue
            i = int(i_val)
            # Draw the main series line
            fig.add_trace(go.Scatter(
                x=series["x_date"],
                y=series["y"][i],
                mode='lines',
                name=f"{pattern_info['selected_series_name']}",
                line={'color': color}
            ))

            sel_name = pattern_info.get("selected_series_name")
            if not sel_name or sel_name not in matched_patterns:
                continue
            for match in matched_patterns[sel_name]:
                if match["score"] is not None and match["score"] <= threshold and min_ws <= match["window_size"] <= max_ws:
                    fig.add_vrect(
                        x0=series["x_date"][match["start_idx"]],
                        x1=min(series["x_date"][match["end_idx"]], series["x_date"][-1]),
                        fillcolor=color,
                        opacity=0.25,
                        layer='below',
                        line_width=1,
                        # annotation_text=f"Match",
                        # annotation_position='top left'
                    )

        fig.update_layout(**layout_style)
        return fig

    @app.callback(
        # Output("submit-sketch", "children"),
        Output("match-results-store", "data"),
        Output("distance-histogram", "figure"),
        Output("distance-threshold-slider", "max"),
        Output("distance-threshold-slider", "value"),
        Output("sketch-history-store", "data"),
        Output("active-sketch-id", "data"),
        Output("auto-select-series", "data"), 
        Output("series-to-sketch-map", "data"),
        Output("active-patterns", "data"),  # <-- Add this output
        Input("submit-sketch", "n_clicks"),
        Input('series-name-filter', 'value'),
        State("sketch-shape-store", "data"),
        State("sketch-history-store", "data"),
        State("window-size-store", "data"),
        State("sketch-color-list", "data"),
        State("active-patterns", "data"),  # <-- Add this line
        prevent_initial_call=True
    )
    def submit_sketch(n_clicks, series_name_filter, shapes, history, window_size, color_list, prev_active_patterns):
        print(f"submit_sketch triggered with n_clicks={n_clicks}, shapes={shapes}, history={history}, window_size={window_size}, series_name_filter={series_name_filter}")
        if not n_clicks or not shapes:
            raise dash.exceptions.PreventUpdate

        sketch_id = str(uuid.uuid4())
        history = history or {} 
        history[sketch_id] = shapes
        print(history)
        name_to_index = {name: i for i, name in enumerate(series["titles"])}

        sketch = np.array(shapes)
        print(series_name_filter)
        topk_matches = query_chroma_topk_for_each_name(history, k=10, filtered_titles=series_name_filter)

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
                if name not in reformatted:
                    reformatted[name] = {}
                if curr_uuid not in reformatted[name]:
                    reformatted[name][curr_uuid] = []
                reformatted[name][curr_uuid].append(entry)

        # Build active_patterns
        if color_list is not None:
            active_patterns = copy.deepcopy(prev_active_patterns) if prev_active_patterns else {}
            color = color_list[(len(history)-1) % len(color_list)]
            matched_patterns = {}
            for name, uuid_dict in reformatted.items():
                for pattern_uuid, matches in uuid_dict.items():
                    matched_patterns[name] = matches
            active_patterns[sketch_id] = {
                "color": color,
                "name": f"Pattern {len(history)}",
                "matched_patterns": matched_patterns,
                "shapes": shapes,
                "window_size": window_size,
                "selected_series": None, 
                "selected_series_name": None
            }

        matched_indices = set()
        for name, uuid_dict in reformatted.items():
            idx = name_to_index.get(name)
            if idx is not None:
                matched_indices.add(str(idx))
                
        series_to_sketch = {}
        for idx, name in enumerate(series["titles"]):
            for sketch_idx, (sketch_id, _) in enumerate(history.items()):
                if name in reformatted and sketch_id in reformatted[name]:
                    series_to_sketch[str(name_to_index[name])] = sketch_idx

        matched_series = list(matched_indices)
        print(f"current window_size = {window_size}")

        hist_fig = go.Figure()
        hist_fig.add_trace(go.Histogram(
            x=all_scores,
            nbinsx=60,
            marker_color="rgba(33, 150, 243, 0.4)",
            marker_line_color="rgba(33, 150, 243, 1)",
            marker_line_width=1,
            opacity=0.85
        ))
        hist_fig.update_layout(
            margin=dict(t=2, b=20, l=0, r=0),
            height=90,  # compact height
            bargap=0.1,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            xaxis=dict(
                showticklabels=True,   # <-- show x-axis labels
                showgrid=False,
                zeroline=False,
                fixedrange=True,
                ticks='',
                linecolor='#e0e0e0',
                linewidth=1,
                title='',              # no title for compactness
                anchor = "y",
                position = 0  # forces x-axis to bottom
            ),
            yaxis=dict(
                visible = False,
                showticklabels=False,
                showgrid=False,
                zeroline=False,
                fixedrange=True,
                ticks='',
                linecolor='#e0e0e0',
                linewidth=1,
            ),
        )

        return (
            # f"Submitted ({len(shapes)} shape{'s' if len(shapes) != 1 else ''})",
            reformatted,
            hist_fig,
            max_dist,
            max_dist,
            history,
            sketch_id,
            matched_series, 
            series_to_sketch,
            active_patterns
        )

    @app.callback(
        Output('sketch-shape-store', 'data'),
        Input('sketch-graph', 'relayoutData'),
        State('sketch-shape-store', 'data')
    )
    def update_sketch_store(relayout_data, current_data):
        print(f"update_sketch_store triggered with relayout_data={relayout_data}, current_data={current_data}")
        if not relayout_data:
            raise dash.exceptions.PreventUpdate

        updated_shapes = parse_and_interpolate_path(relayout_data["shapes"][0]["path"]) if "shapes" in relayout_data else []
        return updated_shapes

    @app.callback(
        Output("distance-threshold-store", "data"),
        Input("distance-threshold-slider", "value")
    )
    def update_threshold_store(value):
        print(f"update_threshold_store triggered with value={value}")
        return value

    @app.callback(
        Output("sketch-graph-container", "children"),
        Input("sketch-refresh-key", "data"),
        State("sketch-history-store", "data"),
        State("sketch-color-list", "data"),
    )
    def render_sketch_graph(refresh_key, history, color_list):
        print("sketch area rendered with refresh key {}".format(refresh_key))
        history = history or {}
        color_list = color_list or ['red']
        next_sketch_idx = len(history)
        sketch_color = color_list[next_sketch_idx % len(color_list)]
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
                            'line': {'color': sketch_color},
                            'fillcolor': 'rgba(0,0,0,0)',
                            'opacity': 0.5
                        },
                        'margin': {'l': 0, 'r': 0, 't': 0, 'b': 0},
                        'xaxis': {'visible': False},
                        'yaxis': {'visible': False},
                        'shapes': [],
                        'annotations': [{
                            'text': "sketch your query here",
                            'xref': "paper",
                            'yref': "paper",
                            'showarrow': False,
                            'font': {'size': 20, 'color': "#bbb", 'family': "Roboto, Arial, sans-serif"},
                            'x': 0.5,
                            'y': 0.5,
                            'xref': 'paper',
                            'yref': 'paper',
                            'xanchor': 'center',
                            'yanchor': 'middle',
                            'opacity': 0.4,
                            'captureevents': False,
                        }]
                    }
                },
                style={
                    'height': '100%',
                    'width': '100%',
                    'minHeight': 0
                }
            )
        ], key=f"{refresh_key}-{sketch_color}", style={'height': '100%', 'minHeight': 0, 'display': 'flex', 'flexDirection': 'column'})

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
        Input("sketch-history-store", "data"),
        Input("sketch-color-list", "data"),
        Input("selected-series-store", "data"),
        Input("series-to-sketch-map", "data"),
        State("active-patterns", "data"),
        State("active-patterns-with-selection", "data")
    )
    def render_sketch_history(history, color_list, selected, series_to_sketch, active_patterns, active_pattern_with_sel):
        if not history:
            return []
        preview_components = []
        for idx, (pattern_uuid, patterns) in enumerate(active_patterns.items()):
            color = color_list[idx % len(color_list)]
            shapes = patterns["shapes"]

            # Use selected_series_name from active_patterns if available
            if pattern_uuid in active_pattern_with_sel:
                selected_series_name = active_pattern_with_sel[pattern_uuid].get("selected_series_name") or "No selection"
            else:
                selected_series_name = "No selection"
            
            preview_fig = {
                'data': [{
                    'x': list(range(len(shapes))),
                    'y': shapes,
                    'mode': 'lines',
                    'line': {'width': 2, 'color': color}
                }],
                'layout': {
                    'height': 68,
                    'width': 72,
                    'autosize': False,
                    'margin': {'l': 0, 'r': 0, 't': 0, 'b': 0},
                    'xaxis': {'visible': False},
                    'yaxis': {'visible': False},
                    'showlegend': False,
                }
            }
            preview_components.append(html.Div([
                html.Button(
                    '×',
                    id={'type': 'remove-sketch', 'index': pattern_uuid},
                    n_clicks=0,
                    style={
                        'position': 'absolute', 'top': '0px', 'right': '0px',
                        'width': '18px', 'height': '18px', 'lineHeight': '16px',
                        'border': 'none', 'borderRadius': '9px', 'background': '#eee', 'cursor': 'pointer',
                        'padding': '0', 'fontSize': '12px', 'color': '#555'
                    }
                ),
                dcc.Graph(
                    figure=preview_fig,
                    config={'staticPlot': True, 'displayModeBar': False, 'responsive': False},
                    style={'height': '68px', 'width': '72px', 'margin': '0'}
                ),
                html.Div(
                    selected_series_name,
                    title=selected_series_name,
                    style={
                        'fontSize': '12px',
                        'textAlign': 'center',
                        'color': 'black',
                        'marginTop': '4px',
                        'height': '16px',
                        'lineHeight': '16px',
                        'whiteSpace': 'nowrap',
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis',
                        'maxWidth': '60px'
                    }
                )
            ], style={'position': 'relative', 'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'rowGap': '4px', 'padding': '4px 6px 2px 6px', 'width': '90px', 'flex': '0 0 90px', 'background': '#fff', 'borderRadius': '8px', 'boxShadow': '0 1px 2px rgba(0,0,0,0.05)'}) )
        return preview_components

    @app.callback(
        Output("active-patterns", "data", allow_duplicate=True),
        Output("sketch-history-store", "data", allow_duplicate=True),
        Output("match-results-store", "data", allow_duplicate=True),
        Output("series-to-sketch-map", "data", allow_duplicate=True),
        Output("active-sketch-id", "data", allow_duplicate=True),
        Input({'type': 'remove-sketch', 'index': ALL}, 'n_clicks'),
        State("active-patterns", "data"),
        State("sketch-history-store", "data"),
        State("match-results-store", "data"),
        State("active-sketch-id", "data"),
        prevent_initial_call=True
    )
    def remove_sketch(n_clicks_list, active_patterns, history, match_data, active_sketch_id):
        ctx = callback_context
        if not ctx.triggered or all(n == 0 or n is None for n in (n_clicks_list or [])):
            raise dash.exceptions.PreventUpdate

        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        removed_id = str(eval(triggered_id)['index'])

        # Remove from active patterns and history
        new_active = dict(active_patterns or {})
        new_active.pop(removed_id, None)

        new_history = dict(history or {})
        new_history.pop(removed_id, None)

        # Filter matches referencing the removed id
        new_match = {}
        if match_data:
            for name, uuid_dict in match_data.items():
                filtered = {uuid: matches for uuid, matches in uuid_dict.items() if str(uuid) != removed_id}
                if filtered:
                    new_match[name] = filtered

        # Rebuild series_to_sketch_map from remaining active patterns
        name_to_index = {name: i for i, name in enumerate(series["titles"])}
        series_to_sketch = {}
        for sketch_idx, (sk_uuid, pat) in enumerate(new_active.items()):
            for name in pat.get("matched_patterns", {}).keys():
                idx = name_to_index.get(name)
                if idx is not None:
                    series_to_sketch[str(idx)] = sketch_idx

        # Update active sketch id if needed
        if active_sketch_id == removed_id:
            new_active_sketch = next(iter(new_active.keys()), None)
        else:
            new_active_sketch = active_sketch_id

        return new_active, new_history, new_match, series_to_sketch, new_active_sketch

    @app.callback(
        Output("window-size-store", "data"),
        Input("window-size-min-input", "value"),
        Input("window-size-max-input", "value"),
        Input("window-size-unit-dropdown", "value"),
    )
    def update_window_size(min_val, max_val, unit):
        print(f"window size updated with min={min_val}, max={max_val}, unit={unit}")
        return [min_val, max_val, unit]

    @app.callback(
        Output("window-size-slider", "min"),
        Output("window-size-slider", "max"),
        Output("window-size-slider", "marks"),
        Output("window-size-slider", "value"),
        Input("match-results-store", "data"),
        State("window-size-unit-dropdown", "value"),
    )
    def update_window_size_slider(match_data, unit):
        print(f"update_window_size_slider triggered with match_data={match_data}, unit={unit}")
        ws_min, ws_max = min(WINDOW_SIZES), max(WINDOW_SIZES)
        # Default to labeled presets (e.g., 7->1w, 14->2w, 30->1m)
        default_marks = {p["value"]: p["label"] for p in WINDOW_PRESETS}
        default_range = [ws_min, ws_max]

        if not match_data:
            return ws_min, ws_max, default_marks, default_range

        # Extract unique window sizes and intersect with known presets
        window_sizes = {
            match.get("window_size")
            for matches_by_uuid in match_data.values()
            for matches in matches_by_uuid.values()
            for match in matches
            if match is not None and match.get("window_size") is not None
        }

        if not window_sizes:
            return ws_min, ws_max, default_marks, default_range

        present_presets = sorted(s for s in window_sizes if s in WINDOW_SIZE_LABELS)
        if not present_presets:
            # Fall back to numeric labels if matches don't align to presets
            sorted_sizes = sorted(window_sizes)
            marks = {size: str(size) for size in sorted_sizes}
            return sorted_sizes[0], sorted_sizes[-1], marks, [sorted_sizes[0], sorted_sizes[-1]]

        marks = {size: WINDOW_SIZE_LABELS[size] for size in present_presets}
        return present_presets[0], present_presets[-1], marks, [present_presets[0], present_presets[-1]]
    
    @app.callback(
        Output('series-name-filter', 'value'),
        Input('series-name-filter', 'value'),
        prevent_initial_call=True
    )
    def update_series_name_filter(new_value):
        print(f"update_series_name_filter triggered with new_value={new_value}")
        return new_value