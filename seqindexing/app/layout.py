from dash import dcc, html
from dash_canvas import DashCanvas
from .layout_components import generate_series_previews
from .data import series, series_x

import numpy as np
np.random.seed(0)


layout = html.Div([
    html.Div([
        html.H1("SeqIndexing Dashboard", style={"textAlign": "center"}),

        # Top Graph Section
        dcc.Graph(
            id="example-plot",
            figure={
                'data': [{'x': series_x, 'y': series[0], 'type': 'line', 'name': 'Sample'}],
                'layout': {'title': 'Example Plot'}
            }
        ),

        # Divider
        html.Hr(style={
            "border": "1px solid #aaa",
            "margin": "20px 0"
        }),

        # Bottom Panel: Series Selector + Sketch Area
        html.Div([
            html.Div([
                html.H3("Select Series"),
                generate_series_previews(series, series_x)
            ], style={
                'flex': '3',
                'padding': '10px',
                'border': '1px solid #ccc',
                'borderRadius': '8px',
                'marginRight': '10px',
                'backgroundColor': '#f9f9f9'
            }),

            # Right Panel (7/10)
            html.Div([
                html.H3("Sketch Area"),
                DashCanvas(
                    id='sketch-area',
                    width=500,
                    height=350,
                    lineWidth=2,
                    lineColor='red',
                    hide_buttons=['zoom', 'pan'],
                )
            ], style={
                'flex': '7',
                'padding': '10px',
                'border': '1px solid #ccc',
                'borderRadius': '8px',
                'backgroundColor': '#f9f9f9'
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
        'backgroundColor': '#fff'
    })
])