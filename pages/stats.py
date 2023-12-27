import json
from dash import dcc, html, dash_table, callback
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import pandas as pd
from datetime import datetime, timedelta
from index import app
from database.models import APICall
from database.helpers import get_records_as_json


# Define the layout for the stats page
def layout():
    return dbc.Container(
        [
            html.H1("API Call Statistics"),
            html.Hr(),
            dbc.Row(id="kpi-cards", className="mb-4"),  # Placeholder for KPI cards
            dbc.Row(
                dbc.Col(
                    id="table",
                    width=12,
                )
            ),
            dcc.Store(id="stats-data"),
        ]
    )


@callback(Output("stats-data", "data"), Input("url", "pathname"))
def update_data(pathname):
    return get_records_as_json(APICall).json


@callback(
    Output("kpi-cards", "children"),
    Input("stats-data", "data"),
    prevent_initial_call=True,
)
def update_kpi_cards(data):
    if data:
        df = pd.DataFrame(data)

        # Convert 'timestamp' column from string to datetime
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # KPIs Calculations
        unique_users = df["username"].nunique()
        recent_calls = df[df["timestamp"] >= (datetime.now() - timedelta(hours=24))]
        calls_last_24h = len(recent_calls)
        most_active_user = df["username"].mode()[0] if not df.empty else "None"
        error_calls = df[df["status_code"] >= 400]
        error_rate = (len(error_calls) / len(df)) * 100 if len(df) > 0 else 0
        most_used_endpoint = df["endpoint"].mode()[0] if not df.empty else "None"
        avg_load_time = df["response_time"].mean() if not df.empty else 0
        df["hour"] = df["timestamp"].dt.hour
        peak_usage_hour = df["hour"].mode()[0] if not df.empty else "None"
        successful_calls = df[df["status_code"].between(200, 299)]
        success_rate = (len(successful_calls) / len(df)) * 100 if len(df) > 0 else 0
        max_response_time = df["response_time"].max() if not df.empty else 0
        method_distribution = df["method"].value_counts().to_dict()

        # Create KPI Cards
        return [
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H5("Unique Users", className="card-title"),
                        html.P(f"{unique_users}", className="card-text"),
                    ]
                ),
                className="m-2",
                style={"width": "18rem"},
            ),
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H5("Calls in Last 24 Hours", className="card-title"),
                        html.P(f"{calls_last_24h}", className="card-text"),
                    ]
                ),
                className="m-2",
                style={"width": "18rem"},
            ),
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H5("Most Active User", className="card-title"),
                        html.P(f"{most_active_user}", className="card-text"),
                    ]
                ),
                className="m-2",
                style={"width": "18rem"},
            ),
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H5("Error Rate", className="card-title"),
                        html.P(f"{error_rate:.2f}%", className="card-text"),
                    ]
                ),
                className="m-2",
                style={"width": "18rem"},
            ),
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H5("Most Used Endpoint", className="card-title"),
                        html.P(f"{most_used_endpoint}", className="card-text"),
                    ]
                ),
                className="m-2",
                style={"width": "18rem"},
            ),
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H5("Average Load Time", className="card-title"),
                        html.P(f"{avg_load_time:.2f} seconds", className="card-text"),
                    ]
                ),
                className="m-2",
                style={"width": "18rem"},
            ),
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H5("Peak Usage Hour", className="card-title"),
                        html.P(f"{peak_usage_hour}:00", className="card-text"),
                    ]
                ),
                className="m-2",
                style={"width": "18rem"},
            ),
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H5("Successful Call Rate", className="card-title"),
                        html.P(f"{success_rate:.2f}%", className="card-text"),
                    ]
                ),
                className="m-2",
                style={"width": "18rem"},
            ),
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H5("Longest Response Time", className="card-title"),
                        html.P(
                            f"{max_response_time:.2f} seconds", className="card-text"
                        ),
                    ]
                ),
                className="m-2",
                style={"width": "18rem"},
            ),
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H5("HTTP Methods Distribution", className="card-title"),
                        html.Ul(
                            [
                                html.Li(f"{method}: {count}")
                                for method, count in method_distribution.items()
                            ]
                        ),
                    ]
                ),
                className="m-2",
                style={"width": "18rem"},
            ),
        ]

    raise PreventUpdate


@callback(
    Output("table", "children"),
    Input("stats-data", "data"),
    prevent_initial_call=True,
)
def update_table(data):
    if data:
        df = pd.DataFrame(data)

        columns = [{"name": col, "id": col} for col in df.columns]
        data = df.to_dict("records")

        return dash_table.DataTable(
            columns=columns,
            data=data,
            filter_action="native",
            sort_action="native",
            page_action="native",
            page_size=10,
        )
