from flask import Flask
from dash import Dash, html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
from api import api
from config import Config
from database.database import db
from pages import stats


# Function to create the Flask app
def create_app():
    flask_app = Flask(__name__)
    flask_app.config.from_object(Config)

    db.init_app(flask_app)

    api.init_app(flask_app)

    with flask_app.app_context():
        db.create_all()

    return flask_app


# Create the Flask app
server = create_app()

# Create the Dash app and bind it to the Flask server
app = Dash(
    __name__,
    server=server,
    title="AIR Server",
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)

# Define the layout of your Dash app
app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        html.Div(id="empty-div-for-title"),
        # header,
        html.Div(
            id="page-content",
            style={
                "flex": 1,
            },
        ),
        # footer,
    ],
    # These settings are used to keep the footer at the end of the page
    style={"display": "flex", "min-height": " 100vh", "flex-direction": "column"},
)


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/stats":
        return stats.layout()

    return "404"  # You could also redirect to a default page layout


app.clientside_callback(
    """
    function(name_path) {
        var nameTab = name_path.charAt(1).toUpperCase() + name_path.slice(2)
        if (name_path === '/') {
            document.title = 'AIR | Home'
        } else {
            document.title = 'AIR | ' + nameTab
        }
    }
    """,
    Output("empty-div-for-title", "children"),
    Input("url", "pathname"),
)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
