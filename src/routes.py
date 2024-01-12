from app import app
from flask import redirect, redirect, request
from flask import request, jsonify
import pandas as pd
import requests
from waitress import serve
from core.data_fetcher import DataFetcher
from core.common import Common
from core.firebase_helpers import FirebaseHelpers
import traceback
import jwt
import json
from components.plots.plot_effecient_frontier import ploteffecientFrontier
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta
from functools import wraps


import firebase_admin
from firebase_admin import credentials, db


with open("secrets-firebase.json") as secrets_file:
    secretsfirebase = json.load(secrets_file)

with open("secrets-google.json") as secrets_file:
    secretsgoogle = json.load(secrets_file)

with open("secrets-tokens.json") as secrets_file:
    secretstokens = json.load(secrets_file)

# Initialize Firebase Admin SDK
cred = credentials.Certificate("secrets-firebase.json")
firebase_admin.initialize_app(cred, {"databaseURL": secretsfirebase["databaseURL"]})


def get_date_n_weekdays_ago(n):
    today = datetime.today().date()
    count = 0
    while count < n:
        today -= relativedelta(days=1)
        if today.weekday() in [1, 2, 3, 4, 5]:
            count += 1
    return today


def authenticate_and_get_user_data(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            access_token = request.cookies.get("jwt_access_token")
            if not access_token:
                return jsonify({"error": "Access token missing"}), 401

            decoded_token = jwt.decode(
                access_token, secretstokens["access_token_secret"], algorithms=["HS256"]
            )
            user_id = decoded_token.get("sub")

            # Pass user_data as a keyword argument to the wrapped function
            kwargs["user_id"] = user_id

            return func(*args, **kwargs)

        except jwt.ExpiredSignatureError:
            refresh_token = request.cookies.get("jwt_refresh_token")
            if not refresh_token:
                return jsonify({"error": "Refresh token missing"}), 401

            try:
                decoded_refresh_token = jwt.decode(
                    refresh_token,
                    secretstokens["refresh_token_secret"],
                    algorithms=["HS256"],
                )
                user_id = decoded_refresh_token.get("sub")

                new_access_token = generate_token(user_id, "access")

                # Return the new access token to the client
                response = jsonify({"access_token": new_access_token})
                return response, 200
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Refresh token expired"}), 401
            except jwt.DecodeError:
                return jsonify({"error": "Invalid refresh token"}), 401

    return wrapper


def update_user_field(user_id, field_name, new_value):
    db_ref = db.reference("users")
    user_ref = db_ref.child(user_id)

    # Update a single field
    user_ref.update({field_name: new_value})


def get_user_data_from_firebase(user_id):
    db_ref = db.reference("users")
    user_ref = db_ref.child(user_id)
    user_data = user_ref.get()

    if user_data:
        return user_data
    else:
        return {}  # Return an empty dictionary or handle as needed


@app.route("/portfolios", methods=["GET"])
def get_ports():
    portfolios_for_plotting = []
    returns = db.reference("tickers").get()
    portfolios = db.reference("portfolios/root").get()

    simulation_style = {
        "fill": True,
        "borderWidth": 2,
        "pointRadius": 2,
        "pointHoverRadius": 20,
        "backgroundColor": "rgba(108, 154, 161, 0.4)",
        "borderColor": "rgba(108, 154, 161, 0.4)",
        "pointBackgroundColor": "rgba(108, 154, 161, 0.4)",
        "pointBorderColor": "rgba(108, 154, 161, 0.4)",
        "hoverBackgroundColor": "rgba(108, 154, 161, 0.4)",
        "hoverBorderColor": "rgba(108, 154, 161, 0.4)",
    }

    benchmark_style = {
        "fill": True,
        "borderWidth": 2,
        "pointRadius": 2,
        "pointHoverRadius": 20,
        "backgroundColor": "rgba(252,153, 153, 0.4)",
        "borderColor": "rgba(252,153, 153, 0.4)",
        "pointBackgroundColor": "rgba(252,153, 153, 0.4)",
        "pointBorderColor": "rgba(252,153, 153, 0.4)",
        "hoverBackgroundColor": "rgba(252,153, 153, 0.4)",
        "hoverBorderColor": "rgba(252,153, 153, 0.4)",
    }

    for index, portfolio_name in enumerate(sorted(portfolios.keys())):
        portfolio = portfolios[portfolio_name]
        benchmarks = portfolio["benchmarks"]
        settings = portfolio["settings"]
        results = portfolio.get("results", None)
        weights_list = []

        if results:
            portfolio_data = {
                "index": index,
                "label": settings.get("name", "Name missing 🤖"),
                "settings": settings,
                "data_weights": [],
                "data_returns": [],
                "data": [],
                "benchmarks": [],
            }
            portfolio_data.update(simulation_style)

            dates_dt = [
                datetime.strptime(date, "%Y-%m-%d").date()
                for date in sorted(results.keys())
            ]
            tickers_history = {}
            for ticker in portfolio["settings"]["tickers"]:
                ticker_history = returns.get(ticker)["historical-data"]
                tickers_history[ticker] = ticker_history

            for date in dates_dt:
                date_string = date.strftime("%Y-%m-%d")
                weights = results[date_string]["optimized_weights"]
                weights_list.append((date, weights))
                portfolio_returns = {}
                for ticker, historical_data in tickers_history.items():
                    portfolio_return =  historical_data.get(date_string, None)
                    if portfolio_return is not None:
                        portfolio_returns[ticker] = portfolio_return["returns"]

                portfolio_data["data_weights"].append({"x": f"{date}", "w": weights})
                portfolio_data["data_returns"].append(
                    {"x": f"{date}", "r": portfolio_returns}
                )

            for index, benchmark_name in enumerate(benchmarks):
                historical_data = returns.get(benchmark_name, {}).get(
                    "historical-data", {}
                )
                benchmark_data = {"index": index, "label": benchmark_name, "data": []}
                benchmark_data.update(benchmark_style)

                for benchmark_date_string, data in historical_data.items():
                    benchmark_date = datetime.strptime(
                        benchmark_date_string, "%Y-%m-%d"
                    ).date()
                    if dates_dt[0] <= benchmark_date <= dates_dt[-1]:
                        benchmark_data["data"].append(
                            {"x": f"{benchmark_date}", "y": data.get("returns")}
                        )

                portfolio_data["benchmarks"].append(benchmark_data)

            portfolios_for_plotting.append(portfolio_data)

    return {"portfolios": portfolios_for_plotting}, 200


def store_user_info(user_info, exclude_fields=None):
    user_id = user_info["id"]  # Assuming 'id' is the user's unique identifier
    db_ref = db.reference("users")
    user_ref = db_ref.child(user_id)

    # Get existing user data
    existing_user_data = user_ref.get()  # Set to an empty dictionary if None

    # Prepare the final updated user data
    updated_user_data = {
        "name": user_info.get("name", ""),
        "verified_email": user_info.get("verified_email", ""),
        "given_name": user_info.get("given_name", ""),
        "family_name": user_info.get("family_name", ""),
        "picture": user_info.get("picture", ""),
        "locale": user_info.get("locale", ""),
        "email": user_info.get("email", ""),
    }
    # Add these fields if we don't know the user already otherwise leave them
    if existing_user_data is None:
        updated_user_data["payment_plan"] = "Free"
        updated_user_data["payment_plan_price"] = 0
        updated_user_data["slots"] = 2

    # Update the user's data in Firebase
    user_ref.update(updated_user_data)


def generate_token(user_id, type, token_expiration):
    # Define your access token secret key (keep it secret!)
    if type == "refresh":
        token_secret = f"{secretstokens['refresh_token_secret']}"
    elif type == "access":
        token_secret = f"{secretstokens['access_token_secret']}"
    else:
        token_secret = None
        token_expiration = datetime.utcnow() - timedelta(minutes=15)

    # Create the payload for the access token
    token_payload = {"sub": user_id, "exp": token_expiration}

    # Generate the access token using JWT
    token = jwt.encode(token_payload, token_secret, algorithm="HS256")
    return token


@app.route("/favicon.ico")
def favicon():
    return "None"


@app.route("/")
def home():
    return f"""Running backend adhoc"""


@app.route("/account/delete", methods=["POST"])
@authenticate_and_get_user_data
def delete_user_data(user_id):
    try:
        # Delete the user's data from Firebase
        db_ref = db.reference("users")
        user_ref = db_ref.child(user_id)
        user_ref.delete()

        # Clear cookies to log the user out
        response = jsonify({"status": "success"})
        response.delete_cookie(
            "jwt_refresh_token",
            path="/",
            domain=f"{app.config['BACKEND_URL']}",
            secure=True,
            samesite="None",
            httponly=True,
        )
        response.delete_cookie(
            "jwt_access_token",
            path="/",
            domain=f"{app.config['BACKEND_URL']}",
            secure=True,
            samesite="None",
            httponly=True,
        )

        return response, 200

    except Exception as e:
        error_message = str(e)
        return jsonify({"error": error_message}), 500


# Define a new route to update fields using a dictionary
@app.route("/account/updateFields", methods=["POST"])
@authenticate_and_get_user_data
def update_fields(user_id):
    try:
        fields_and_values = request.json

        if not fields_and_values or not isinstance(fields_and_values, dict):
            return jsonify({"error": "Invalid fields and values data"}), 400

        # Update the specified fields for the user in Firebase
        for field, new_value in fields_and_values.items():
            update_user_field(user_id, field, new_value)

        return (
            jsonify({"status": "success", "message": "Fields updated successfully"}),
            200,
        )

    except Exception as e:
        error_message = str(e)
        return jsonify({"status": "error", "message": error_message}), 500


@app.route("/auth/callback")
def google_callback():
    # Extract the authorization code from the query parameters
    authorization_code = request.args.get("code")
    # Set up the token exchange request
    token_url = "https://oauth2.googleapis.com/token"
    token_params = {
        "code": authorization_code,
        "client_id": secretsgoogle["client_id"],
        "client_secret": secretsgoogle["client_secret"],
        "redirect_uri": f"{app.config['BACKEND_PROTOCOL']}{app.config['BACKEND_URL']}{app.config['BACKEND_PORT']}{secretsgoogle['redirect_path']}",
        "grant_type": "authorization_code",
    }

    # Exchange authorization code for access token and refresh token
    token_response = requests.post(token_url, data=token_params)
    token_data = token_response.json()

    # print('Token Data:', token_data)  # Add this line to see the token data
    access_token = token_data.get("access_token")
    # refresh_token = token_data.get("refresh_token")  # Get the refresh token

    # Use the access token to fetch user data
    user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    user_info_response = requests.get(user_info_url, headers=headers)
    user_info = user_info_response.json()

    # Store user data in Firebase Realtime Database
    exclude_fields = ["payment_plan", "payment_plan_price", "slots"]
    store_user_info(user_info, exclude_fields)

    redirect_uri = f"{app.config['FRONTEND_PROTOCOL']}{app.config['FRONTEND_URL']}{app.config['FRONTEND_PORT']}/#/"
    expiration_refresh = datetime.utcnow() + timedelta(minutes=60)
    expiration_access = datetime.utcnow() + timedelta(minutes=15)

    # Set JWT tokens as HttpOnly and Secure cookies
    response = redirect(redirect_uri)
    response.set_cookie(
        "jwt_refresh_token",
        generate_token(user_info["id"], "refresh", expiration_refresh),
        httponly=True,
        secure=True,
        domain=f"{app.config['BACKEND_URL']}",
        path="/",
        samesite="None",
        expires=expiration_refresh,  # Set the expiration time
    )
    response.set_cookie(
        "jwt_access_token",
        generate_token(user_info["id"], "access", expiration_access),
        httponly=True,
        secure=True,
        domain=f"{app.config['BACKEND_URL']}",
        path="/",
        samesite="None",
        expires=expiration_access,  # Set the expiration time
    )
    return response


@app.route("/auth/logout", methods=["GET"])
@authenticate_and_get_user_data
def auth_logout(user_id):
    response = jsonify({"message": "Logged out"})

    response.delete_cookie(
        "jwt_refresh_token",
        path="/",
        domain=f"{app.config['BACKEND_URL']}",
        secure=True,
        samesite="None",
        httponly=True,
    )
    response.delete_cookie(
        "jwt_access_token",
        path="/",
        domain=f"{app.config['BACKEND_URL']}",
        secure=True,
        samesite="None",
        httponly=True,
    )

    return response, 200


@app.route("/auth/verify-token", methods=["GET"])
@authenticate_and_get_user_data
def auth_verify_token(user_id):
    # Access token is valid, fetch user data from Firebase
    user_data = get_user_data_from_firebase(user_id)

    return jsonify({"message": "Access token valid", "user_data": user_data}), 200


@app.route("/valid_tickers", methods=["GET"])
# @authenticate_and_get_user_data
def get_valid_tickers():
    valid_tickers = []
    try:
        ref = db.reference("tickers")
        tickers = ref.get()
        for symbol, ticker_data in tickers.items():
            historical_data = ticker_data.get("historical-data", {})

            if historical_data:
                newest_date = max(historical_data.keys())
                newest_price = historical_data[newest_date]['prices']
                valid_tickers.append(
                    {
                        "ticker": FirebaseHelpers.firebase_ticker_decode(symbol),
                        "price": round(newest_price, 2),
                        "name":  'popname: '+FirebaseHelpers.firebase_ticker_decode(symbol), 
                        "price_from_date": newest_date,
                    }
                )
        response_data = {
            "status": "success",
            "data": valid_tickers,
        }

        return jsonify(response_data), 200  # 200 OK status code for successful response

    except Exception as e:
        error_message = str(e)
        response_data = {"status": "error", "message": error_message}

        return (
            jsonify(response_data),
            500,
        )  # 500 Internal Server Error status code for errors


@app.route("/crunch_data", methods=["POST"])
@authenticate_and_get_user_data
def crunch_data(user_id):
    try:
        # Get the data from the request
        data = request.json
        print(data)
        # Perform your data processing here...
        # For example, you can access the form data like this:
        stocks = data.get("stocks")
        lookback = int(data.get("numberOfDays"))
        extrapolate = int(data.get("extrapolate"))
        risk_free_rate = float(data.get("percentValue"))
        # Generate analysis-data
        symbols = [stock["ticker"] for stock in stocks]
        lookback_day = get_date_n_weekdays_ago(lookback + 1)
        days_since_lookback_day = date.today() - lookback_day
        data = DataFetcher(
            symbols, lookback=relativedelta(days=days_since_lookback_day.days), db=db
        )
        
        analysis = Common().generate_analysis_data(
            prices=data.data["prices"],
            returns=data.data["returns"],
            lookback=lookback,
            scale=extrapolate,
            stocks=stocks,
            risk_free_rate=risk_free_rate,
        )

        portfolios_data = Common().build_portfolios(analysis=analysis)

        figs = {
            # "Prices": plotPrices(analysis).data,
            # "Returns": plotReturns(analysis).data,
            # "Covariances": plotCovariances(analysis).data,
            # "Cumulative returns": plotCumulativeReturns(portfolios_data=portfolios_data, analysis=analysis, comparison=None).data,
            "Efficient Frontier": ploteffecientFrontier(
                portfolios_data=portfolios_data, analysis=analysis, comparison=None
            ).data,
        }

        # Now you can process the data as needed and return the result
        # For this example, I'll just return a simple response
        response_data = {"message": "Data processed successfully!", "data": figs}
        return jsonify(response_data), 200

    except Exception as e:
        # Handle any errors that may occur during data processing
        traceback_info = traceback.format_exc()  # Get the traceback as a string
        error_message = str(e)
        return jsonify({"error": error_message, "traceback": traceback_info}), 500

