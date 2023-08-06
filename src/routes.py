from app import app
from flask import Flask, redirect, url_for, abort, redirect, request
from flask import render_template, request, jsonify, current_app
import pandas as pd
import plotly.offline as pyo
import datetime as dt
from components.fetch_data_component import DataFetcher
from components.fetch_data_component import InfoFetcher
from components.fetch_data_component import Fetcher
from components.fetch_data_component import Common
from components.fetch_data_component import Settings
from dateutil.relativedelta import relativedelta
from functools import wraps
import json
import traceback

from components.plots.plot_covariances import plotCovariances
from components.plots.plot_effecient_frontier import ploteffecientFrontier
from components.plots.plot_prices import plotPrices
from components.plots.plot_returns import plotReturns
from components.plots.plot_benchmark import plotBenchmark
import requests
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol

from flask import session


@app.route("/favicon.ico")
def favicon():
    return "None"


@app.route("/")
def home():
    return "Running"


# @app.route('/', methods=['POST'])
# def handle_request():
#    # Read the headers of the incoming request
#    headers = request.headers
#
#    # Verify the required information in the headers for exchanging information
#    required_info = 'Your_Agreed_Information'
#    if 'Your_Agreed_Header_Field' not in headers or headers['Your_Agreed_Header_Field'] != required_info:
#        return 'Invalid request', 400
#
#    # Process the request and return the response
#    return 'Request processed successfully'


@app.route("/crunch_data_test", methods=["POST"])
def crunch_data_test():
    try:
        Fetcher(app)

        # Get the data from the request
        data = request.json

        # Perform your data processing here...
        # For example, you can access the form data like this:
        lookback = int(data.get("numberOfDays"))
        percentValue = float(data.get("percentValue"))
        extrapolate = int(data.get("extrapolate"))
        stocks = data.get("stocks")

        # Calculate total value of the request
        total_value = 0
        for stock in stocks:
            current_price = float(stock["currentPrice"])
            held_stocks = int(stock["heldStocks"])
            total_value += current_price * held_stocks
        # Ensure the program still works if total_value = 0 (prevent devision by 0)
        if total_value == 0:
            total_value = 1

        analysis = Common().append_to_df(
            df=pd.DataFrame(
                {
                    "ticker": [stock["ticker"] for stock in stocks],
                    "ratio": [
                        (float(stock["currentPrice"]) * int(stock["heldStocks"]))
                        / total_value
                        for stock in stocks
                    ],
                }
            ).set_index(["ticker"]),
            data=current_app.data,
            lookback=lookback,
            extrapolate=extrapolate,
            tickers=[stock["ticker"] for stock in stocks],
        )

        figs = {
            # "Prices": plotPrices(analysis).data,
            # "Returns": plotReturns(analysis).data,
            # "Covariances": plotCovariances(analysis).data,
            "Efficient Frontier": ploteffecientFrontier(analysis, None).data,
        }

        # Now you can process the data as needed and return the result
        # For this example, I'll just return a simple response
        response_data = {"message": "Data processed successfully!", "data": figs}
        print("Returning processed data")
        return jsonify(response_data), 200

    except Exception as e:
        # Handle any errors that may occur during data processing
        traceback_info = traceback.format_exc()  # Get the traceback as a string
        error_message = str(e)
        print(error_message)
        print(traceback_info)
        return jsonify({"error": error_message, "traceback": traceback_info}), 500


if __name__ == "__main__":
    app.run(debug=True)
