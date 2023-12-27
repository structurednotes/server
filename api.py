import time
import json
import random
import logging
from uuid import uuid4
from datetime import datetime as dt
from flask_restx import Api, Resource
from database.models import db, APICall
from database.helpers import add_record
from flask import request


api = Api(
    prefix="/api",
    title="AIR Excel API",
    description="Details of the AIR API for Excel Fucntions",
    doc="/swagger/",
    contact_email="pierre.bichon@bofa.com",
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

ns_air = api.namespace("air", description="AIR Pricing operations")

air_parser = api.parser()
air_parser.add_argument(
    "parameters",
    help="The set of Pricing Parameters Names of your payoff (Underlyings, Maturity, Currency, ...)",
)
air_parser.add_argument(
    "values",
    help="The set of Pricing Parameters Values of your payoff (SPX Index, 2y, USD, ...)",
)
air_parser.add_argument("option1", help="Optional parameter")
air_parser.add_argument("option2", help="Optional parameter")
air_parser.add_argument("culture")
air_parser.add_argument("UserName", location="headers")
air_parser.add_argument("Machine", location="headers")


def remove_empty_rows_and_cols(data):
    """
    Remove empty rows and columns from a list of lists.

    Parameters:
        data (list of list): The input list of lists.

    Returns:
        list of list: The cleaned list of lists.
    """
    # Remove empty rows
    data = [row for row in data if any(row)]

    if not data:
        return []

    # Transpose the list of lists to make columns become rows
    transposed = zip(*data)

    # Remove empty columns (which are now rows)
    transposed = [row for row in transposed if any(row)]

    # Transpose the list of lists back to its original orientation
    return list(map(list, zip(*transposed)))


def replace_empty_values(data, replacement=""):
    """
    Replace any empty or None values in a list of lists with an empty string.

    Parameters:
        data (list of list): The input list of lists.
        replacement (string or float): The value replacing empty values.

    Returns:
        list of list: The list of lists with empty or None values replaced.
    """
    return [
        [item if item not in [None, {}, [], ""] else replacement for item in row]
        for row in data
    ]


def clean_json_values(args, key):
    # Get the values from the POST request arguments
    result = args.get(key) or '[["#N/A"]]'
    result = json.loads(result)

    # Delete empty values from inputs
    result = remove_empty_rows_and_cols(result)

    # Replace empty values
    result = replace_empty_values(result, replacement="")

    return result


def transpose(data: list) -> list:
    """
    Transpose a list of lists.

    Parameters:
        data (list of list): The input list of lists.

    Returns:
        list of list: The transposed list of lists.
    """
    return list(map(list, zip(*data)))


@ns_air.route("")
@api.doc(description="Endpoint to handle AIR Pricing")
class AirPricing(Resource):
    @api.expect(air_parser)
    @api.doc(responses={200: "Success", 400: "Validation Error", 403: "Not Authorized"})
    def post(self):
        start_time = time.time()  # Start timer to measure response time

        args = air_parser.parse_args()
        machine = args.get("Machine", "Unknown Machine")
        username = args.get("UserName", "Unknown User")
        client_ip = request.remote_addr
        endpoint = "/api/air"
        method = request.method
        user_agent = request.headers.get("User-Agent", "Unknown")
        referrer = request.headers.get("Referer", "Unknown")

        # Read and process parameters and values
        parameters = clean_json_values(args, "parameters")
        values = clean_json_values(args, "values")

        # Prepare log message with User Details
        msg = f"AIR Pricing by {username} from {machine} - parameters: {parameters} - values: {values}"

        try:
            # Read optional parameters
            option1 = args.get("option1")
            if option1:
                option1 = option1.lower()

            option2 = args.get("option2")
            if option2:
                option2 = option2.lower()

            # Orientation of the Pricing Grid
            pricing_orientation = "rows"
            if parameters and len(parameters) > len(parameters[0]):
                pricing_orientation = "columns"

                # Transpose the corresponding Parameters and Values
                parameters = transpose(parameters)
                values = transpose(values)

            # Turn the inputs to list of pricings
            pricings = [{x: y for x, y in zip(parameters[0], z)} for z in values]

            # Initialize Results and Results Type
            data = []

            for pricing in pricings:
                data.append(
                    [
                        {"Value": f"AIR - {uuid4()}", "Type": "string"},
                        {"Value": 1 + random.random(), "Type": "float"},
                        {"Value": dt.today().strftime("%Y-%m-%d"), "Type": "date"},
                        # {"Value": dt.today(), "Type": "date"},
                    ],
                )

            logging.info(msg)

            # Calculate response time
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds

            # Log the successful API call to the database
            add_record(
                APICall,
                machine=machine,
                username=username,
                client_ip=client_ip,
                endpoint=endpoint,
                method=method,
                user_agent=user_agent,
                referrer=referrer,
                parameters=json.dumps(args),  # Serialize args to JSON string
                response_time=response_time,
                status_code=200,  # Assuming success at this point
                # response_body can be added
            )

            return {"data": data}

        except Exception as e:
            # Log the error message
            logging.error(f"Error processing AIR Pricing: {str(e)} - {msg}")

            # Log the failed API call to the database
            add_record(
                APICall,
                machine=machine,
                username=username,
                client_ip=client_ip,
                endpoint=endpoint,
                method=method,
                user_agent=user_agent,
                referrer=referrer,
                parameters=json.dumps(args) if args else None,
                response_time=(time.time() - start_time) * 1000,
                status_code=500,  # Internal Server Error
                error_message=str(e),
                # response_body can be added
            )

            data = [[{"Value": f"AIR Error: {e}", "Type": "string"}]]

            return {"data": data}


# Registering the resource with the API
api.add_resource(AirPricing, "/air")
