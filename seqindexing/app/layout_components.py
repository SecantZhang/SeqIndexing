from dash import dcc, html
from dash_canvas import DashCanvas


def generate_series_previews(series, series_x):
    return html.Div([
        html.Div([
            dcc.Checklist(
                id='series-selector',
                options=[{'label': f'Series {i}', 'value': str(i)} for i in range(len(series))],
                value=[],  # initially nothing selected
                labelStyle={'display': 'block', 'margin': '4px'}
            )
        ], style={'marginBottom': '10px'}),

        html.Div([
            dcc.Graph(
                id=f"preview-{i}",
                figure={
                    'data': [{'x': series_x[::10], 'y': series[i][::10], 'mode': 'lines', 'line': {'width': 1}}],
                    'layout': {
                        'height': 80,
                        'margin': dict(l=10, r=10, t=10, b=10),
                        'xaxis': {'visible': False},
                        'yaxis': {'visible': False},
                        'showlegend': False
                    }
                },
                config={'displayModeBar': False},
                style={'height': '80px'}
            )
            for i in range(len(series))
        ], style={
            'height': '300px',
            'overflowY': 'scroll'
        })
    ])