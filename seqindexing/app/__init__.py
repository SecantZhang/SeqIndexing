from flask import Flask, redirect
import dash
from .layout import layout
from .callbacks import register_callbacks


def create_app():
    server = Flask(__name__)
    dash_app = dash.Dash(
        __name__,
        server=server,
        url_base_pathname='/dashboard/',
        meta_tags=[
            {"name": "viewport", "content": "width=device-width, initial-scale=1, maximum-scale=1"}
        ],
    )

    dash_app.layout = layout
    register_callbacks(dash_app)

    @server.route('/')
    def _root_redirect():
        return redirect('/dashboard/')

    @server.route('/dashboard')
    def _dashboard_no_slash_redirect():
        return redirect('/dashboard/')

    return server