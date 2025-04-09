from flask import Flask
import dash
from .layout import layout
from .callbacks import register_callbacks


def create_app():
    server = Flask(__name__)
    dash_app = dash.Dash(__name__, server=server, url_base_pathname='/dashboard/')

    dash_app.layout = layout
    register_callbacks(dash_app)

    return server