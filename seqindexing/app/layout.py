from dash import dcc, html
from dash_canvas import DashCanvas
from .layout_components import generate_series_previews
from .data import series, series_x
from .config import (
    FONT_FAMILY, TITLE_FONT_SIZE, LABEL_FONT_SIZE, PREVIEW_FONT_SIZE, SMALL_FONT_SIZE,
    PREVIEW_HEIGHT, PREVIEW_CARD_HEIGHT,
    SELECTED_BORDER, UNSELECTED_BORDER, BACKGROUND_COLOR
)

import numpy as np
np.random.seed(0)


layout = html.Div([
    html.Div([
        html.H1("SeqIndexing Dashboard", style={
            "textAlign": "center",
            "fontFamily": FONT_FAMILY,
            "fontSize": TITLE_FONT_SIZE
        }),

        # Top Graph Section
        dcc.Graph(
            id="example-plot",
            figure={
                'data': [{'x': series_x, 'y': series[0], 'type': 'line', 'name': 'Sample'}],
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
                    'minHeight': '0'
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
                'fontFamily': FONT_FAMILY
            }),

            # Right Panel (7/10)
            html.Div([
                dcc.Tabs(
                    id="sketch-tab-manager",
                    value=None,  # no tab selected at first
                    children=[],
                    persistence=True,
                    persistence_type="session"
                ),
                dcc.Store(id="sketch-history-store", data={}),
                dcc.Store(id="active-sketch-id", data=None),

                html.H3("Sketch Area", style={
                    'fontFamily': FONT_FAMILY,
                    'fontSize': LABEL_FONT_SIZE,
                    'marginBottom': '10px'
                }),
                dcc.Graph(
                    id='sketch-graph',
                    config={
                        'modeBarButtonsToAdd': [
                            'drawline',
                            'drawopenpath',
                            'drawclosedpath',
                            'drawcircle',
                            'drawrect',
                            'eraseshape'
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
                ),
                dcc.Store(id='sketch-shape-store'),
                dcc.Store(id='distance-threshold-store', data=1.0),
                html.Button("Submit", id="submit-sketch", n_clicks=0, style={
                    'marginTop': '10px',
                    'fontSize': SMALL_FONT_SIZE
                }),
                html.Div([
                    html.Div([
                        dcc.Graph(
                            id="distance-histogram",
                            config={"displayModeBar": False},
                            style={"height": "90px", "padding": "0", "margin": "0"}
                        ),
                        dcc.Slider(
                            id="distance-threshold-slider",
                            min=0,
                            max=1,
                            step=0.01,
                            value=1.0,
                            tooltip={"always_visible": False},
                            updatemode="drag",
                            className="custom-slider",
                            marks={}
                        )
                    ], style={
                        'marginTop': '10px',
                        'padding': '4px 0',
                        'width': '100%',
                        'boxSizing': 'border-box'
                    })
                ], style={
                    'marginTop': '12px',
                    'padding': '6px',
                    'borderTop': '1px solid #ccc',
                    'height': '140px'
                })
            ], style={
                'flex': '7',
                'padding': '10px',
                'border': UNSELECTED_BORDER,
                'borderRadius': '8px',
                'backgroundColor': BACKGROUND_COLOR,
                'fontFamily': FONT_FAMILY,
                'overflow': 'hidden',
                'maxWidth': '100%',
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