from dash import dcc, html
from .data import series
from .config import (
    FONT_FAMILY, TITLE_FONT_SIZE, LABEL_FONT_SIZE, SMALL_FONT_SIZE,
    PREVIEW_CARD_HEIGHT, UNSELECTED_BORDER, BACKGROUND_COLOR
)
from .utils import get_color_palette

import numpy as np
np.random.seed(0)

N_SKETCHES = 20
color_list = get_color_palette(N_SKETCHES)
initial_selection = []

layout = html.Div([
    dcc.Store(id="sketch-color-list", data=color_list),
    dcc.Store(id="sketch-selection-list", data=initial_selection),
    dcc.Store(id="series-to-sketch-map", data={}),
    dcc.Store(id="active-patterns", data={}),
    dcc.Store(id="active-patterns-with-selection", data={}),
    html.Div([
        html.Div("SeqIndexing Dashboard", className="material-title", style={"textAlign": "center"}),
        dcc.Graph(
            id="example-plot",
            figure={
                'data': [{'x': series["x"], 'y': series["y"][0], 'type': 'line', 'name': 'Sample'}],
                'layout': {'title': 'Example Plot'}
            },
            style={'fontFamily': 'Roboto, Arial, sans-serif'}
        ),
        html.Hr(className="material-divider"),
        html.Div([
            dcc.Store(id="auto-select-series", data=[]),
            # Sidebar
            html.Div([
                html.Div("Select Series", className="material-section-title"),
                dcc.Store(id='selected-series-store', data=[]),
                dcc.Store(id='match-results-store', data={}),
                html.Div(
                    id='series-selector-container',
                    style={
                        'overflowY': 'auto',
                        'flex': '1 1 0%',
                        'minHeight': 0,
                        'display': 'flex',
                        'flexDirection': 'column',
                        'gap': '8px',
                        'minWidth': '180px',
                        'width': '100%',
                    }
                )
            ], className="material-card material-sidebar", style={
                "display": "flex",
                "flexDirection": "column",
                "height": "100%",
                "minHeight": 0,
                "flex": "0 0 260px",
                "maxWidth": "300px",
                "marginBottom": 0  # <-- Add this line to override .material-card margin-bottom
            }),
            # Main
            html.Div([
                dcc.Store(id="sketch-history-store", data={}),
                dcc.Store(id="active-sketch-id", data=None),
                html.Div("Sketch Area", className="material-section-title"),
                html.Div([
                    dcc.Dropdown(
                        id='series-name-filter',
                        options=[{'label': name, 'value': name} for name in series["titles"]],
                        value=[],
                        multi=True,
                        placeholder="Select stock names to display...",
                        className="material-dropdown",
                        style={'flex': 7}
                    ),
                    dcc.Dropdown(
                        id='distance-measure-dropdown',
                        options=[
                            {'label': 'Euclidean', 'value': 'euclidean'},
                            {'label': 'DTW', 'value': 'dtw'},
                            {'label': 'Qetch', 'value': 'qetch'}
                        ],
                        value='euclidean',
                        clearable=False,
                        className="material-dropdown",
                        style={'flex': 3}
                    ),
                ], className="material-flex-row", style={'marginBottom': '8px'}),
                html.Div([
                    html.Div("History", className="material-label", style={'marginBottom': '4px'}),
                    html.Div(id="sketch-history-list", className="material-history")
                ]),
                dcc.Store(id="sketch-refresh-key", data=0),
                html.Div(id="sketch-graph-container"),
                dcc.Store(id='sketch-shape-store'),
                dcc.Store(id='distance-threshold-store', data=1.0),
                dcc.Store(id="window-size-store", data=7),
                html.Div([
                    html.Button("Submit", id="submit-sketch", n_clicks=0, className="material-btn"),
                    html.Button("Clear", id="refresh-sketch", n_clicks=0, className="material-btn secondary"),
                    html.Div([
                        html.Label("Window Size", className="material-label"),
                        html.Div(
                            dcc.RangeSlider(
                                id="window-size-slider",
                                step=1,
                                marks=None,
                                value=[7, 30],
                                allowCross=False,
                                tooltip={"placement": "top", "always_visible": False},
                                className="material-slider"
                            ),
                            style={'flexGrow': 1}
                        )
                    ], className="material-flex-row", style={'width': '100%'})
                ], className="material-flex-row", style={'marginTop': '10px'}),
                html.Div([
                    html.Div([
                        dcc.Graph(
                            id="distance-histogram",
                            config={"displayModeBar": False},
                            style={"height": "80px", "margin": "0", "padding": "0"}
                        ),
                        dcc.Slider(
                            id="distance-threshold-slider",
                            min=0,
                            max=6,
                            step=0.01,
                            value=1.0,
                            updatemode="drag",
                            className="material-slider",
                            marks={0: '0', 6: 'Max'},
                            included=False
                        )
                    ], className="material-flex-col", style={'marginTop': '10px', 'padding': '0 6px'})
                ], style={
                    'marginTop': '12px',
                    'padding': '6px 0',
                    'borderTop': '1px solid #eee',
                    'height': '140px'
                })
            ], className="material-card material-main"),
        ], style={
            'display': 'flex',
            'flexDirection': 'row',
            'alignItems': 'stretch',
            'height': '800px',
            'minHeight': 0,
            'gap': '20px'  # <-- Add this line for more space between sidebar and main
        }),
    ], className="material-container")
])