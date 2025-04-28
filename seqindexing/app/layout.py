# layout.py  –  two-column layout with scrolling Select-Series card
from dash import dcc, html
from .data   import series
from .utils  import get_color_palette
import numpy as np
np.random.seed(0)

# card height ratios (left & right columns share them)
BIG_RATIO   = 1   # main plot / sketch canvas
SMALL_RATIO = 1   # select-series / history               (sum = 1.0)

N_SKETCHES        = 20
color_list        = get_color_palette(N_SKETCHES)
initial_selection = []

# Top bar with title
top_bar = html.Div(
    style={
        "width": "100%",
        "background": "#fff",
        "padding": "0 0 0 0",
        "height": "56px",
        "display": "flex",
        "alignItems": "center",
        "boxShadow": "0 2px 8px rgba(0,0,0,0.04)",
        "marginBottom": "18px",
        "borderRadius": "10px"
    },
    children=[
        html.Div(
            "SeqIndexing Dashboard",
            style={
                "fontWeight": "bold",
                "fontSize": "1.5rem",
                "color": "#222",
                "marginLeft": "32px",
                "fontFamily": "Roboto, Arial, sans-serif"
            }
        )
    ]
)

layout = html.Div(
    className="material-container",
    style={
        "height":     "1200px",  # Reduced overall height
        "width":      "99vw",
        "maxWidth":   "99vw",
        "margin":     "0",
        "overflow":   "hidden",
        "display":    "flex",
        "flexDirection": "column",
        "rowGap":     "0",
        "padding":    "40px 64px",
        "background": "#f7f8fa",
        "boxSizing":  "border-box"
    },
    children=[
        top_bar,

        # workspace (fills remaining height)
        html.Div(
            style={
                "flex": "1 1 0%",
                "display": "flex",
                "flexDirection": "row",
                "alignItems": "stretch",
                "gap": "24px",
                "minHeight": 0,
                "height": "100%",
                "width": "100%",           # Make workspace fill available width
                "maxWidth": "100%",        # Remove width limit
                "margin": "0",             # Remove auto-centering
                "boxSizing": "border-box"
            },
            children=[
                # ═════════ MAIN PLOT (LEFT PANEL, 5/10) ═════════
                html.Div(
                    style={
                        "flex": "5 5 0%",
                        "minWidth": 0,
                        "background": "#fff",
                        "borderRadius": "14px",
                        "boxShadow": "0 2px 12px rgba(0,0,0,0.06)",
                        "padding": "28px 24px",
                        "display": "flex",
                        "flexDirection": "column",
                        "justifyContent": "center",
                        "height": "100%",
                        "boxSizing": "border-box"
                    },
                    children=[
                        html.Div("Interactive Series Presenter", className="material-section-title", style={
                            "fontWeight": "bold",
                            "fontSize": "1.1rem",
                            "marginBottom": "12px",
                            "color": "#333"
                        }),
                        html.Div(
                            style={"flex": f"1 1 0%", "minWidth": 0, "minHeight": 0},
                            children=[
                                dcc.Graph(
                                    id="example-plot",
                                    figure=dict(
                                        data=[dict(
                                            x=series["x"],
                                            y=series["y"][0],
                                            type="line",
                                            name=series["titles"][0],
                                            line={'color': "#2196f3"}
                                        )],
                                        layout=dict(
                                            title="Active Patterns and Their Matches",
                                            title_font=dict(family="Roboto, Arial, sans-serif", size=22, color="#212121"),
                                            # Remove fixed height to allow responsiveness
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
                                            xaxis=dict(
                                                rangeslider=dict(visible=True, thickness=0.07, bgcolor="#f5f5f5"),
                                                type='linear',
                                                showgrid=True,
                                                gridcolor='#eeeeee',
                                                zeroline=False,
                                                linecolor='#bdbdbd',
                                                linewidth=1,
                                                tickfont=dict(family="Roboto, Arial, sans-serif", size=13, color="#616161"),
                                                title_font=dict(family="Roboto, Arial, sans-serif", size=15, color="#757575"),
                                            ),
                                            yaxis=dict(
                                                showgrid=True,
                                                gridcolor='#eeeeee',
                                                zeroline=False,
                                                linecolor='#bdbdbd',
                                                linewidth=1,
                                                tickfont=dict(family="Roboto, Arial, sans-serif", size=13, color="#616161"),
                                                title_font=dict(family="Roboto, Arial, sans-serif", size=15, color="#757575"),
                                            ),
                                            plot_bgcolor='#fff',
                                            paper_bgcolor='#fff',
                                            font=dict(family="Roboto, Arial, sans-serif", color="#212121"),
                                            hoverlabel=dict(
                                                bgcolor="#fafafa",
                                                font_size=13,
                                                font_family="Roboto, Arial, sans-serif"
                                            )
                                        )
                                    ),
                                    config={"responsive": True},  # Enable responsiveness
                                    style={
                                        "height": "100%",
                                        "width": "100%",
                                        "minWidth": 0
                                    }
                                )
                            ]
                        )
                    ]
                ),

                # ═════════ SELECT SERIES PANEL (MIDDLE PANEL, 2/10) ═════════
                html.Div(
                    className="material-card",
                    style={
                        "flex": "2 2 0%",
                        "minWidth": 0,
                        "background": "#f9fafb",
                        "borderRadius": "14px",
                        "padding": "24px 18px",
                        "display": "flex",
                        "flexDirection": "column",
                        "height": "100%",
                        "overflow": "hidden",
                        "boxSizing": "border-box"
                    },
                    children=[
                        dcc.Store(id="auto-select-series", data=[]),
                        dcc.Store(id="selected-series-store", data=[]),
                        dcc.Store(id="match-results-store", data={}),
                        html.Div("Select Series", className="material-section-title", style={
                            "fontWeight": "bold",
                            "fontSize": "1.1rem",
                            "marginBottom": "12px",
                            "color": "#333"
                        }),
                        html.Div(
                            id="series-selector-container",
                            style={
                                "overflowY": "auto",
                                "flex": "1 1 0%",
                                "rowGap": "4px",
                                "paddingRight": "4px",
                                "minHeight": 0
                            }
                        )
                    ]
                ),

                # ═════════ SKETCH AREA (RIGHT PANEL, 3/10) ═════════
                html.Div(
                    style={
                        "flex": "3 3 0%",
                        "minWidth": 0,
                        "display": "flex",
                        "flexDirection": "column",
                        "height": "100%",              # Ensure same height as other columns
                        "alignSelf": "stretch",        # Stretch to match parent height
                        "boxSizing": "border-box", 
                        "marginBottom": "0",
                    },
                    children=[
                        html.Div(
                            className="material-card",
                            style={
                                "flex": "1 1 0%",      # Take all available height in the column
                                "display": "flex",
                                "flexDirection": "column",
                                "minWidth": 0,
                                "minHeight": 0,
                                "background": "#f9fafb",  # Match middle column
                                "borderRadius": "14px",
                                "boxShadow": "0 2px 12px rgba(0,0,0,0.06)",
                                "padding": "24px 18px",
                                "boxSizing": "border-box", 
                                "marginBottom": "0",
                            },
                            children=[
                                # History at the top
                                html.Div("History",
                                         className="material-label",
                                         style={"marginBottom": "4px", "fontWeight": "bold", "color": "#333"}),
                                html.Div(
                                    id="sketch-history-list",
                                    className="material-history",
                                    style={
                                        "overflowY": "auto",
                                        "flex": "0 0 60px",
                                        "marginBottom": "12px"
                                    }
                                ),

                                # Sketch controls and canvas
                                dcc.Store(id="sketch-history-store", data={}),
                                dcc.Store(id="active-sketch-id", data=None),
                                dcc.Store(id="sketch-refresh-key", data=0),
                                dcc.Store(id="sketch-shape-store"),
                                dcc.Store(id="distance-threshold-store", data=1.0),
                                dcc.Store(id="window-size-store", data=7),
                                html.Div("Series Filters",
                                         className="material-label",
                                         style={"marginBottom": "10px", "marginTop": "12px", "fontWeight": "bold", "color": "#333"}),
                                html.Div(
                                    className="material-flex-row",
                                    style={"marginBottom": "8px"},
                                    children=[
                                        dcc.Dropdown(
                                            id="series-name-filter",
                                            options=[{"label": n, "value": n} for n in series["titles"]],
                                            value=[],
                                            multi=True,
                                            placeholder="Select stock names…",
                                            # className="material-dropdown",
                                            style={"flex": 7, 
                                                   "border": "none"}
                                        ),
                                        dcc.Dropdown(
                                            id="distance-measure-dropdown",
                                            options=[
                                                {"label": "Euclidean", "value": "euclidean"},
                                                {"label": "DTW", "value": "dtw"},
                                                {"label": "Qetch", "value": "qetch"}],
                                            value="euclidean",
                                            clearable=False,
                                            # className="material-dropdown",
                                            style={"flex": 3,
                                                   "border": "none"}
                                        )
                                    ]
                                ),

                                html.Div("Sketch Canvas",
                                         className="material-label",
                                         style={"marginBottom": "10px", "marginTop": "12px", "fontWeight": "bold", "color": "#333"}),
                                # Sketch canvas in the middle
                                html.Div(id="sketch-graph-container", 
                                         style={"flex": "1 1 0%",
                                                "minHeight": 0,
                                                "marginBottom": "12px",
                                                "borderRadius": "10px",         # Add rounded corners
                                                "overflow": "hidden"            # Ensure child respects border radius
                                            }
                                        ),

                                # Controls at the bottom
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
                                    style={"marginTop": "10px", 
                                           "height": "60px",},
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
                                                    "always_visible": False
                                                },
                                                className="material-slider"
                                            ),
                                            style={
                                                "flexGrow": 1,
                                                "border": "none",        # ✅ Style the wrapper
                                                "background": "#fff"
                                            }
                                        )
                                    ]
                                ),

                                html.Div(
                                    className="material-flex-col",
                                    style={
                                        "marginTop": "10px",
                                        "borderRadius": "10px",    # Add rounded corners to the histogram box
                                        "overflow": "hidden"       # Ensure child respects border radius
                                    },
                                    children=[
                                        dcc.Graph(
                                            id="distance-histogram",
                                            config={"displayModeBar": False},
                                            style={
                                                "height": "120px",
                                                "width": "100%",
                                                "minWidth": 0,
                                                "margin": 0,
                                                "padding": 0
                                            }
                                        ),
                                        html.Div(
                                            dcc.Slider(
                                                id="distance-threshold-slider",
                                                min=0, max=6, step=0.01, value=1.0,
                                                updatemode="drag",
                                                className="material-slider",
                                                marks={0: "0", 6: "Max"},
                                                included=False
                                            ),
                                            style={"flexGrow": 1,
                                                   "border": "none",        # ✅ Style the wrapper
                                                   "background": "#fff"})
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        ),

        # shared hidden stores
        dcc.Store(id="sketch-color-list", data=color_list),
        dcc.Store(id="sketch-selection-list", data=initial_selection),
        dcc.Store(id="series-to-sketch-map", data={}),
        dcc.Store(id="active-patterns", data={}),
        dcc.Store(id="active-patterns-with-selection", data={})
    ]
)
