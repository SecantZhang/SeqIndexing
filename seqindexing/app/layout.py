# layout.py – main plot 75 %  |  history 25 % (horizontal previews);
#             right column with restored gaps.
from dash import dcc, html
from .data import series
from .utils import get_color_palette
import numpy as np

np.random.seed(0)

# ── add these two constants near the top of layout.py ─────────────
APP_W = "2000px"      # overall width  (change to taste)
APP_H = "1200px"       # overall height (change to taste)
# ── column shares ─────────────────────────────────────────────────
LEFT_PLOT_RATIO, LEFT_HISTORY_RATIO = 0.85, 0.15        # left column
RIGHT_CTRL_RATIO, RIGHT_SELECT_RATIO, RIGHT_SKETCH_RATIO = 0.12, 0.25, 0.63
# thumbnails are resized by assets/history_previews.css
# ──────────────────────────────────────────────────────────────────

N_SKETCHES = 20
color_list = get_color_palette(N_SKETCHES)
initial_selection = []

# ── top bar ───────────────────────────────────────────────────────
top_bar = html.Div(
    "SeqIndexing Dashboard",
    style={
        "height": "48px",
        "display": "flex",
        "alignItems": "center",
        "padding": "0 32px",
        "fontWeight": "bold",
        "fontSize": "1.6rem",
        "background": "#fff",
        "borderRadius": "8px",
        "boxShadow": "0 2px 6px rgba(0,0,0,0.05)",
    },
)

# ── layout ────────────────────────────────────────────────────────
layout = html.Div(
    style={
        "width": APP_W,
        "height": APP_H,
        "margin": "32px auto",  # centred in viewport
        "display": "flex",
        "flexDirection": "column",
        "rowGap": "16px",
        "background": "#f2f4f7",
        "borderRadius": "14px",
        "boxShadow": "0 4px 16px rgba(0,0,0,0.1)",
        "overflow": "hidden",  # prevent outer scrollbars
    },
    children=[
        top_bar,
        # ── workspace grid ─────────────────────────────────────────
        html.Div(
            style={
                "flex": "1 1 0%",
                "display": "grid",
                "gridTemplateColumns": "minmax(0,5fr) minmax(0,3fr)",
                "gap": "24px",
                "minHeight": 0,
            },
            children=[
                # ═════════ LEFT COLUMN ═════════
                html.Div(
                    style={
                        "display": "flex",
                        "flexDirection": "column",
                        "height": "100%",
                        "minWidth": 0,
                        "minHeight": 0,
                    },
                    children=[
                        # ① main plot
                        html.Div(
                            style={
                                "flex": f"{LEFT_PLOT_RATIO} 1 0%",
                                "background": "#fff",
                                "borderRadius": "12px",
                                "padding": "20px",
                                "boxShadow": "0 2px 10px rgba(0,0,0,0.06)",
                                "minWidth": 0,
                                "minHeight": 0,
                            },
                            children=[
                                dcc.Graph(
                                    id="example-plot",
                                    figure={
                                        "data": [
                                            {
                                                "x": series["x"],
                                                "y": series["y"][0],
                                                "type": "line",
                                                "name": series["titles"][0],
                                                "line": {"color": "#2196f3"},
                                            }
                                        ],
                                        "layout": {
                                            "margin": {"t": 20, "l": 30, "r": 10, "b": 32},
                                            "plot_bgcolor": "#fff",
                                            "paper_bgcolor": "#fff",
                                            "xaxis": {"showgrid": True, "gridcolor": "#e0e0e0"},
                                            "yaxis": {"showgrid": True, "gridcolor": "#e0e0e0"},
                                        },
                                    },
                                    config={"responsive": True},
                                    style={"height": "100%", "width": "100%", "minWidth": 0},
                                )
                            ],
                        ),
                        # ② history panel
                        html.Div(
                            style={
                                "flex": f"{LEFT_HISTORY_RATIO} 1 0%",
                                "background": "#fff",
                                "borderRadius": "12px",
                                "padding": "18px 16px",
                                "marginTop": "16px",
                                "boxShadow": "0 2px 10px rgba(0,0,0,0.06)",
                                "display": "flex",
                                "flexDirection": "column",
                                "minWidth": 0,
                                "minHeight": 0,
                            },
                            children=[
                                html.Div(
                                    "History",
                                    style={"fontWeight": "bold", "marginBottom": "6px"},
                                ),
                                html.Div(
                                    id="sketch-history-list",
                                    style={
                                        "display": "flex",
                                        "flexDirection": "row",
                                        "columnGap": "12px",
                                        "overflowX": "auto",
                                        "overflowY": "hidden",
                                        "flex": "1 1 0%",
                                        "minHeight": 0,
                                    },
                                ),
                            ],
                        ),
                    ],
                ),
                # ═════════ RIGHT COLUMN ═════════
                html.Div(
                    style={
                        "display": "flex",
                        "flexDirection": "column",
                        "height": "100%",
                        "minWidth": 0,
                        "minHeight": 0,
                        "rowGap": "16px",          # restored spacing
                    },
                    children=[
                        # ③ query controls
                        html.Div(
                            style={
                                "flex": f"{RIGHT_CTRL_RATIO} 1 0%",
                                "background": "#fff",
                                "borderRadius": "12px",
                                "padding": "18px 16px",
                                "boxShadow": "0 2px 10px rgba(0,0,0,0.06)",
                                "display": "flex",
                                "flexDirection": "column",
                                "rowGap": "10px",
                                "minWidth": 0,
                                "minHeight": 0,
                            },
                            children=[
                                html.Div("Query Controls", style={"fontWeight": "bold"}),
                                dcc.Dropdown(
                                    id="series-name-filter",
                                    options=[{"label": n, "value": n} for n in series["titles"]],
                                    value=[],
                                    multi=True,
                                    placeholder="Select stock names…",
                                    style={"border": "none"},
                                ),
                                dcc.Dropdown(
                                    id="distance-measure-dropdown",
                                    options=[
                                        {"label": "Euclidean", "value": "euclidean"},
                                        {"label": "DTW", "value": "dtw"},
                                        {"label": "Qetch", "value": "qetch"},
                                    ],
                                    value="euclidean",
                                    clearable=False,
                                    style={"border": "none"},
                                ),
                            ],
                        ),
                        # ④ series selector
                        html.Div(
                            style={
                                "flex": f"{RIGHT_SELECT_RATIO} 1 0%",
                                "background": "#fff",
                                "borderRadius": "12px",
                                "padding": "18px 12px",
                                "boxShadow": "0 2px 10px rgba(0,0,0,0.06)",
                                "display": "flex",
                                "flexDirection": "column",
                                "overflow": "hidden",
                                "minWidth": 0,
                                "minHeight": 0,
                            },
                            children=[
                                html.Div("Select Series", style={"fontWeight": "bold", "marginBottom": "8px"}),
                                dcc.Store(id="auto-select-series", data=[]),
                                dcc.Store(id="selected-series-store", data=[]),
                                dcc.Store(id="match-results-store", data={}),
                                html.Div(
                                    id="series-selector-container",
                                    style={
                                        "overflowY": "auto",
                                        "flex": "1 1 0%",
                                        "rowGap": "4px",
                                        "paddingRight": "4px",
                                        "minHeight": 0,
                                    },
                                ),
                            ],
                        ),
                        # ⑤ sketch canvas + controls
                        html.Div(
                            style={
                                "flex": f"{RIGHT_SKETCH_RATIO} 1 0%",
                                "background": "#fff",
                                "borderRadius": "12px",
                                "padding": "18px 16px",
                                "boxShadow": "0 2px 10px rgba(0,0,0,0.06)",
                                "display": "flex",
                                "flexDirection": "column",
                                "minWidth": 0,
                                "minHeight": 0,
                            },
                            children=[
                                # hidden stores (unchanged) ………………………………………
                                dcc.Store(id="sketch-history-store", data={}),
                                dcc.Store(id="active-sketch-id", data=None),
                                dcc.Store(id="sketch-refresh-key", data=0),
                                dcc.Store(id="sketch-shape-store"),
                                dcc.Store(id="distance-threshold-store", data=1.0),
                                dcc.Store(id="window-size-store", data=7),

                                # title
                                html.Div("Sketch Canvas",
                                         style={"fontWeight": "bold", "marginBottom": "6px"}),

                                # canvas gets almost all card height
                                html.Div(id="sketch-graph-container",
                                         style={
                                             "flex": "1 1 auto",  # ← expands
                                             "minHeight": 0,
                                             "marginBottom": "0"  # no gap below canvas
                                         }),

                                # ───────── compact footer ─────────
                                html.Div(
                                    style={
                                        "flex": "0 0 150px",  # ← only 150 px high
                                        "display": "flex",
                                        "flexDirection": "column",
                                        "rowGap": "8px"
                                    },
                                    children=[

                                        # ① buttons
                                        html.Div(
                                            style={"display": "flex", "columnGap": "8px"},
                                            children=[
                                                html.Button("Submit", id="submit-sketch",
                                                            n_clicks=0, className="material-btn",
                                                            style={"flex": "1 1 0%"}),
                                                html.Button("Clear", id="refresh-sketch",
                                                            n_clicks=0, className="material-btn secondary",
                                                            style={"flex": "1 1 0%"})
                                            ]
                                        ),

                                        # ② window-size slider
                                        html.Label("Window Size"),
                                        dcc.RangeSlider(
                                            id="window-size-slider",
                                            step=1, value=[7, 30], allowCross=False,
                                            tooltip={"placement": "top"}, className="material-slider"
                                        ),

                                        # ③ histogram (shorter) + threshold slider
                                        dcc.Graph(
                                            id="distance-histogram",
                                            config={"displayModeBar": False},
                                            style={
                                                "height": "60px",  # ← was 110 px
                                                "width": "100%",
                                                "minWidth": 0,
                                                "margin": 0
                                            }
                                        ),
                                        dcc.Slider(
                                            id="distance-threshold-slider",
                                            min=0, max=6, step=0.01, value=1.0,
                                            updatemode="drag",
                                            marks={0: "0", 6: "Max"},
                                            included=False,
                                            className="material-slider"
                                        ),
                                    ]
                                )
                            ]
                        ),
                    ],
                ),
            ],
        ),
        # ─── global hidden stores ───
        dcc.Store(id="sketch-color-list", data=color_list),
        dcc.Store(id="sketch-selection-list", data=initial_selection),
        dcc.Store(id="series-to-sketch-map", data={}),
        dcc.Store(id="active-patterns", data={}),
        dcc.Store(id="active-patterns-with-selection", data={}),
    ],
)
