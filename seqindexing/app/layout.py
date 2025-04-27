from dash import dcc, html
from dash_canvas import DashCanvas
from .layout_components import generate_series_previews
from .data import series
from .config import (
    FONT_FAMILY, TITLE_FONT_SIZE, LABEL_FONT_SIZE, PREVIEW_FONT_SIZE, SMALL_FONT_SIZE,
    PREVIEW_HEIGHT, PREVIEW_CARD_HEIGHT,
    SELECTED_BORDER, UNSELECTED_BORDER, BACKGROUND_COLOR
)
from .utils import get_color_palette

import numpy as np
np.random.seed(0)


N_SKETCHES = 20  # or your expected max number of sketches
color_list = get_color_palette(N_SKETCHES)
initial_selection = []


layout = html.Div([
    dcc.Store(id="sketch-color-list", data=color_list),
    dcc.Store(id="sketch-selection-list", data=initial_selection),
    dcc.Store(id="series-to-sketch-map", data={}),
    dcc.Store(id="active-patterns", data={}),
    dcc.Store(id="active-patterns-with-selection", data={}),
    html.Div([
        html.H1("SeqIndexing Dashboard", style={
            "textAlign": "center",
            "fontFamily": FONT_FAMILY,
            "fontSize": TITLE_FONT_SIZE,
            "margin": "3px 0 3px 0"
        }),

        # Top Graph Section
        dcc.Graph(
            id="example-plot",
            figure={
                'data': [{'x': series["x"], 'y': series["y"][0], 'type': 'line', 'name': 'Sample'}],
                'layout': {'title': 'Example Plot'}
            },
            style={
                'fontFamily': FONT_FAMILY
            }
        ),

        # Divider
        html.Hr(style={
            "border": "1px solid #aaa",
            "margin": "20px 0"
        }),

        # Bottom Panel: Series Selector + Sketch Area
        html.Div([
            dcc.Store(id="auto-select-series", data=[]),
            # Left Panel (3/10)
            html.Div([
                html.H3("Select Series", style={
                    'fontFamily': FONT_FAMILY,
                    'fontSize': LABEL_FONT_SIZE,
                }),
                dcc.Store(id='selected-series-store', data=[]),
                dcc.Store(id='match-results-store', data={}),
                html.Div(id='series-selector-container', style={
                    'height': f'{PREVIEW_CARD_HEIGHT * 4.5}px',  # rough estimate for visible cards
                    'overflowY': 'auto',
                    'flexGrow': '1',
                    'display': 'flex',
                    'flexDirection': 'column',
                    'gap': '8px',
                    'minHeight': '0',
                    'minWidth': '180px'   # ensure sidebar never collapses too small
                })
            ], style={
                'flex': '3',
                'display': 'flex',
                'flexDirection': 'column',
                'padding': '10px',
                'border': UNSELECTED_BORDER,
                'borderRadius': '8px',
                'marginRight': '10px',
                'backgroundColor': BACKGROUND_COLOR,
                'fontFamily': FONT_FAMILY,
                'minWidth': '200px'       # fixed sidebar width
            }),

            # Right Panel (7/10)
            html.Div([
                dcc.Store(id="sketch-history-store", data={}),
                dcc.Store(id="active-sketch-id", data=None),

                html.H3("Sketch Area", style={
                    'fontFamily': FONT_FAMILY,
                    'fontSize': LABEL_FONT_SIZE,
                    'marginBottom': '10px'
                }),
                dcc.Dropdown(
                    id='series-name-filter',
                    options=[{'label': name, 'value': name} for name in series["titles"]],
                    value=[],  # all selected by default
                    multi=True,
                    placeholder="Select stock names to display...",
                    style={
                        'fontSize': '12px',
                        'maxHeight': '60px'
                    }
                ),
                html.Div([
                    html.H4("History", style={'fontSize': LABEL_FONT_SIZE, 'marginBottom': '4px'}),
                    html.Div(id="sketch-history-list", style={
                        'display': 'flex',
                        'flexWrap': 'wrap',
                        'gap': '6px',
                        'marginBottom': '10px'
                    })
                ]),
                dcc.Store(id="sketch-refresh-key", data=0),  # allows forced re-render
                html.Div(id="sketch-graph-container"),  # placeholder for dynamic sketchpad
                dcc.Store(id='sketch-shape-store'),
                dcc.Store(id='distance-threshold-store', data=1.0),
                dcc.Store(id="window-size-store", data=7),
                html.Div([
                    # Buttons
                    html.Button("Submit", id="submit-sketch", n_clicks=0, style={
                        'fontSize': SMALL_FONT_SIZE,
                        'marginRight': '6px'
                    }),
                    html.Button("Clear", id="refresh-sketch", n_clicks=0, style={
                        'fontSize': SMALL_FONT_SIZE,
                        'marginRight': '10px'
                    }),

                    html.Div([
                        html.Label("Window Size", style={
                            'fontSize': SMALL_FONT_SIZE,
                            'marginRight': '8px',
                            'whiteSpace': 'nowrap'
                        }),
                        html.Div(
                            dcc.RangeSlider(
                                id="window-size-slider",
                                step=None,
                                marks={7: '7', 30: '30'},  # dynamically set
                                value=[7, 30],
                                allowCross=False,
                                tooltip={"placement": "top", "always_visible": True},
                                className="custom-slider"
                            ),
                            style={
                                'flexGrow': 1,
                                # 'minWidth': '250px',
                                # 'maxWidth': '100%',
                            }
                        )
                    ], style={
                        'display': 'flex',
                        'alignItems': 'center',
                        'width': '100%',
                        'gap': '12px'
                    }),
                ], style={
                    'display': 'flex',
                    'alignItems': 'center',
                    'marginTop': '10px',
                    'gap': '10px'
                }),
                html.Div([
                    html.Div([
                        dcc.Graph(
                            id="distance-histogram",
                            config={"displayModeBar": False},
                            style={
                                "height": "80px",
                                "margin": "0",
                                "padding": "0"
                            }
                        ),
                        dcc.Slider(
                            id="distance-threshold-slider",
                            min=0,
                            max=6,
                            step=0.01,
                            value=1.0,
                            # tooltip={"always_visible": False},
                            updatemode="drag",
                            className="custom-slider",
                            marks={
                                0: '0',
                                6: 'Max'
                            },  # keep it clean
                            included=False  # remove fill color
                        )
                    ], style={
                        'display': 'flex',
                        'flexDirection': 'column',
                        'gap': '6px',
                        'marginTop': '10px',
                        'padding': '0 6px'
                    })
                ], style={
                    'marginTop': '12px',
                    'padding': '6px 0',
                    'borderTop': '1px solid #eee',
                    'height': '140px'
                })
            ], style={
                'flex': '7',
                'display': 'flex',
                'flexDirection': 'column',
                'padding': '10px',
                'border': UNSELECTED_BORDER,
                'borderRadius': '8px',
                'backgroundColor': BACKGROUND_COLOR,
                'fontFamily': FONT_FAMILY,
                'overflow': 'hidden',
                'boxSizing': 'border-box'
            })
        ], style={
            'display': 'flex',
            'marginTop': '10px'
        })

    ], style={
        'maxWidth': '1000px',
        'margin': '0 auto',
        'padding': '20px',
        'border': '2px solid #666',
        'borderRadius': '12px',
        'boxShadow': '0px 2px 8px rgba(0,0,0,0.1)',
        'backgroundColor': '#fff',
        'fontFamily': FONT_FAMILY
    })
])