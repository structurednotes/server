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
                        html.P(
                            f"{avg_load_time:.2f} milliseconds", className="card-text"
                        ),
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
                            f"{max_response_time:.2f} milliseconds",
                            className="card-text",
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

        # Convert Timestamp from string to datetime and format it
        df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # Convert Response Time from milliseconds to seconds and round to 3 decimal places
        df["response_time"] = (df["response_time"] / 1000).round(3)

        data = df.to_dict("records")

        columns = [
            {"name": "ID", "id": "id"},
            {"name": "Timestamp", "id": "timestamp"},
            {"name": "Username", "id": "username"},
            {"name": "Endpoint", "id": "endpoint"},
            {"name": "Parameters", "id": "parameters"},
            {"name": "Response Time (seconds)", "id": "response_time"},
            {"name": "Method", "id": "method"},
            {"name": "User Agent", "id": "user_agent"},
            {"name": "Client IP", "id": "client_ip"},
            {"name": "Error Message", "id": "error_message"},
            {"name": "Machine", "id": "machine"},
            {"name": "Referrer", "id": "referrer"},
            {"name": "Response Body", "id": "response_body"},
            {"name": "Status Code", "id": "status_code"},
        ]

        return dash_table.DataTable(
            columns=columns,
            data=data,
            filter_action="native",
            sort_action="native",
            sort_mode="single",  # or "multi" for multi-column sort
            sort_by=[
                {"column_id": "id", "direction": "desc"}
            ],  # Sort by 'id' in descending order
            page_action="native",
            page_size=20,  # Display 20 rows per page
            style_table={
                "maxWidth": "100%",
                "overflowX": "auto",
            },  # Table takes max 100% width
            style_cell={  # Allow cells to be resized and add padding
                "minWidth": "100px",
                "width": "100px",
                "maxWidth": "180px",
                "overflow": "hidden",
                "textOverflow": "ellipsis",
                "padding": "10px",
            },
            style_data={  # Add borders and padding to data cells
                "border": "1px solid lightgrey",
                "borderRadius": "4px",
                "padding": "5px",
            },
            style_header={  # Add styling to header cells
                "border": "1px solid black",
                "backgroundColor": "lightgrey",
                "fontWeight": "bold",
                "borderRadius": "4px",
                "padding": "5px",
            },
            editable=False,
            column_selectable="single",  # Allow only single column to be selected, use "multi" for multiple columns
            row_selectable="multi",  # Allow multiple rows to be selected
            hidden_columns=[
                "client_ip",
                "method",
                "error_message",
                "machine",
                "referrer",
                "response_body",
                "user_agent",
            ],  # Hiding specific columns
        )
