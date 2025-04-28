# layout.py  –  two-column layout with scrolling Select-Series card
from dash import dcc, html
from .data   import series
from .utils  import get_color_palette
import numpy as np
np.random.seed(0)

# card height ratios (left & right columns share them)
BIG_RATIO   = 0.60   # main plot / sketch canvas
SMALL_RATIO = 0.40   # select-series / history               (sum = 1.0)

N_SKETCHES        = 20
color_list        = get_color_palette(N_SKETCHES)
initial_selection = []

layout = html.Div(
    className="material-container",
    style={
        "height":     "100vh",      # full viewport (no outer scroll)
        "width":      "100%",
        "maxWidth":   "100vw",
        "margin":     "0 auto",
        "overflow":   "hidden",
        "display":    "flex",
        "flexDirection": "column",
        "rowGap":     "16px",
        "padding":    "12px 24px"
    },
    children=[

        html.Div("SeqIndexing Dashboard",
                 className="material-title",
                 style={"textAlign": "center"}),

        # workspace  (fills remaining height)
        html.Div(
            style={
                "flex":                "1 1 0%",
                "display":             "grid",
                "gridTemplateColumns": "minmax(0,4fr) minmax(0,2fr)",
                "gap":                 "24px",
                "minHeight":           0
            },
            children=[

                # ═════════ LEFT COLUMN ═════════
                html.Div(style={"minWidth": 0, "height": "100%"}, children=[
                    html.Div(
                        style={
                            "display":       "flex",
                            "flexDirection": "column",
                            "height":        "100%",  # ← same as right
                            "minWidth":      0,
                            "minHeight":     0
                        },
                        children=[

                            # main plot
                            html.Div(
                                style={"flex": f"{BIG_RATIO} 1 0%",
                                       "minWidth": 0, "minHeight": 0},
                                children=[
                                    dcc.Graph(
                                        id="example-plot",
                                        figure=dict(
                                            data=[dict(
                                                x=series["x"],
                                                y=series["y"][0],
                                                type="line",
                                                name="Sample")],
                                            layout=dict(title="Example Plot")
                                        ),
                                        config={"responsive": True},
                                        style={
                                            "height":   "100%",
                                            "width":    "100%",
                                            "minWidth": 0
                                        }
                                    )
                                ]
                            ),

                            # Select-Series (now forced to scroll)
                            html.Div(
                                className="material-card",
                                style={
                                    "flex":      f"{SMALL_RATIO} 1 0%",
                                    "display":   "flex",
                                    "flexDirection": "column",
                                    "overflow":  "hidden",   # ← key line
                                    "minWidth":  0,
                                    "minHeight": 0
                                },
                                children=[
                                    dcc.Store(id="auto-select-series",    data=[]),
                                    dcc.Store(id="selected-series-store", data=[]),
                                    dcc.Store(id="match-results-store",   data={}),

                                    html.Div("Select Series",
                                             className="material-section-title"),

                                    html.Div(
                                        id="series-selector-container",
                                        style={
                                            "overflowY":  "auto",
                                            "flex":       "1 1 0%",
                                            "rowGap":     "4px",
                                            "paddingRight": "4px",
                                            "minHeight":  0
                                        }
                                    )
                                ]
                            )
                        ]
                    )
                ]),

                # ═════════ RIGHT COLUMN ═════════
                html.Div(style={"minWidth": 0, "height": "100%"}, children=[
                    html.Div(
                        style={
                            "display":       "flex",
                            "flexDirection": "column",
                            "height":        "100%",  # match left column
                            "minWidth":      0,
                            "minHeight":     0
                        },
                        children=[

                            # sketch canvas
                            html.Div(
                                className="material-card",
                                style={
                                    "flex": f"{BIG_RATIO} 1 0%",
                                    "display":    "flex",
                                    "flexDirection": "column",
                                    "minWidth":   0,
                                    "minHeight":  0
                                },
                                children=[
                                    dcc.Store(id="sketch-history-store",      data={}),
                                    dcc.Store(id="active-sketch-id",          data=None),
                                    dcc.Store(id="sketch-refresh-key",        data=0),
                                    dcc.Store(id="sketch-shape-store"),
                                    dcc.Store(id="distance-threshold-store",  data=1.0),
                                    dcc.Store(id="window-size-store",         data=7),

                                    html.Div(
                                        className="material-flex-row",
                                        style={"marginBottom": "8px"},
                                        children=[
                                            dcc.Dropdown(
                                                id="series-name-filter",
                                                options=[{"label": n, "value": n}
                                                         for n in series["titles"]],
                                                value=[],
                                                multi=True,
                                                placeholder="Select stock names…",
                                                className="material-dropdown",
                                                style={"flex": 7}
                                            ),
                                            dcc.Dropdown(
                                                id="distance-measure-dropdown",
                                                options=[
                                                  {"label": "Euclidean","value": "euclidean"},
                                                  {"label": "DTW",      "value": "dtw"},
                                                  {"label": "Qetch",    "value": "qetch"}],
                                                value="euclidean",
                                                clearable=False,
                                                className="material-dropdown",
                                                style={"flex": 3}
                                            )
                                        ]
                                    ),

                                    html.Div(id="sketch-graph-container",
                                             style={"flex": "1 1 0%",
                                                    "minHeight": 0})
                                ]
                            ),

                            # history / controls
                            html.Div(
                                className="material-card",
                                style={
                                    "flex": f"{SMALL_RATIO} 1 0%",
                                    "display":    "flex",
                                    "flexDirection": "column",
                                    "minWidth":   0,
                                    "minHeight":  0
                                },
                                children=[
                                    html.Div("History",
                                             className="material-label",
                                             style={"marginBottom": "4px"}),

                                    html.Div(id="sketch-history-list",
                                             className="material-history",
                                             style={
                                                 "overflowY": "auto",
                                                 "flex":      "0 0 60px"}),

                                    html.Div(
                                        className="material-flex-row",
                                        style={"marginTop": "6px"},
                                        children=[
                                            html.Button("Submit",
                                                        id="submit-sketch",
                                                        n_clicks=0,
                                                        className="material-btn"),
                                            html.Button("Clear",
                                                        id="refresh-sketch",
                                                        n_clicks=0,
                                                        className="material-btn secondary")
                                        ]
                                    ),

                                    html.Div(
                                        className="material-flex-row",
                                        style={"marginTop": "10px"},
                                        children=[
                                            html.Label("Window Size",
                                                       className="material-label"),
                                            html.Div(
                                                dcc.RangeSlider(
                                                    id="window-size-slider",
                                                    step=1, value=[7, 30],
                                                    allowCross=False,
                                                    tooltip={
                                                        "placement": "top",
                                                        "always_visible": False},
                                                    className="material-slider"),
                                                style={"flexGrow": 1}
                                            )
                                        ]
                                    ),

                                    html.Div(
                                        className="material-flex-col",
                                        style={"marginTop": "10px"},
                                        children=[
                                            dcc.Graph(
                                                id="distance-histogram",
                                                config={"displayModeBar": False},
                                                style={
                                                    "height":  "70px",
                                                    "width":   "100%",
                                                    "minWidth": 0,
                                                    "margin":  0,
                                                    "padding": 0}),
                                            dcc.Slider(
                                                id="distance-threshold-slider",
                                                min=0, max=6, step=0.01, value=1.0,
                                                updatemode="drag",
                                                className="material-slider",
                                                marks={0: "0", 6: "Max"},
                                                included=False)
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                ])
            ]
        ),

        # shared hidden stores
        dcc.Store(id="sketch-color-list",              data=color_list),
        dcc.Store(id="sketch-selection-list",          data=initial_selection),
        dcc.Store(id="series-to-sketch-map",           data={}),
        dcc.Store(id="active-patterns",                data={}),
        dcc.Store(id="active-patterns-with-selection", data={})
    ]
)
