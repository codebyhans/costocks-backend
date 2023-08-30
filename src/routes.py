from app import app
from flask import Flask, redirect, url_for, abort, redirect, request
from flask import render_template, request, jsonify, current_app
import pandas as pd
import requests
from waitress import serve
from components.fetch_data_component import DataFetcher
from components.fetch_data_component import Fetcher
from components.fetch_data_component import Common
import traceback
import jwt
import json
from components.plots.plot_covariances import plotCovariances
from components.plots.plot_effecient_frontier import ploteffecientFrontier
from components.plots.plot_prices import plotPrices
from components.plots.plot_returns import plotReturns
from components.plots.plot_benchmark import plotBenchmark
from datetime import datetime, timedelta
import time
from functools import wraps



import firebase_admin
from firebase_admin import credentials, db


with open("src/secrets-firebase.json") as secrets_file:
    secretsfirebase = json.load(secrets_file)

with open("src/secrets-google.json") as secrets_file:
    secretsgoogle = json.load(secrets_file)


with open("src/secrets-tokens.json") as secrets_file:
    secretstokens = json.load(secrets_file)

# Initialize Firebase Admin SDK
cred = credentials.Certificate("src/secrets-firebase.json")
firebase_admin.initialize_app(cred, {"databaseURL": secretsfirebase["databaseURL"]})

def authenticate_and_get_user_data(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            access_token = request.cookies.get('jwt_access_token')
            if not access_token:
                return jsonify({'error': 'Access token missing'}), 401

            decoded_token = jwt.decode(access_token, secretstokens['access_token_secret'], algorithms=['HS256'])
            user_id = decoded_token.get('sub')

            # Pass user_data as a keyword argument to the wrapped function
            kwargs['user_id'] = user_id

            return func(*args, **kwargs)
        
        except jwt.ExpiredSignatureError:
            refresh_token = request.cookies.get('jwt_refresh_token')
            if not refresh_token:
                return jsonify({'error': 'Refresh token missing'}), 401

            try:
                decoded_refresh_token = jwt.decode(refresh_token, secretstokens['refresh_token_secret'], algorithms=['HS256'])
                user_id = decoded_refresh_token.get('sub')
                
                new_access_token = generate_token(user_id, 'access')

                # Return the new access token to the client
                response = jsonify({'access_token': new_access_token})
                return response, 200
            except jwt.ExpiredSignatureError:
                return jsonify({'error': 'Refresh token expired'}), 401
            except jwt.DecodeError:
                return jsonify({'error': 'Invalid refresh token'}), 401
    
    return wrapper


def update_user_field(user_id, field_name, new_value):
    db_ref = db.reference("users")
    user_ref = db_ref.child(user_id)

    # Update a single field
    user_ref.update({
        field_name: new_value
    })

def get_user_data_from_firebase(user_id):
    db_ref = db.reference("users")
    user_ref = db_ref.child(user_id)
    user_data = user_ref.get()

    if user_data:
        return user_data 
    else:
        return {}  # Return an empty dictionary or handle as needed

def store_user_info(user_info, exclude_fields=None):
    user_id = user_info["id"]  # Assuming 'id' is the user's unique identifier
    db_ref = db.reference("users")
    user_ref = db_ref.child(user_id)

    # Get existing user data
    existing_user_data = user_ref.get()   # Set to an empty dictionary if None

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
    return f"""Running"""


@app.route('/account/delete', methods=['POST'])
@authenticate_and_get_user_data
def delete_user_data(user_id):
    try:
        # Delete the user's data from Firebase
        db_ref = db.reference("users")
        user_ref = db_ref.child(user_id)
        user_ref.delete()

        # Clear cookies to log the user out
        response = jsonify({'status': 'success'})
        response.delete_cookie('jwt_refresh_token', path='/', domain=f"{app.config['BACKEND_URL']}", secure=True, samesite=None, httponly=True)
        response.delete_cookie('jwt_access_token', path='/', domain=f"{app.config['BACKEND_URL']}", secure=True, samesite=None, httponly=True)

        return response, 200

    except Exception as e:
        error_message = str(e)
        return jsonify({'error': error_message}), 500

# Define a new route to update fields using a dictionary
@app.route('/account/updateFields', methods=['POST'])
@authenticate_and_get_user_data
def update_fields(user_id):
    try:
        fields_and_values = request.json

        if not fields_and_values or not isinstance(fields_and_values, dict):
            return jsonify({'error': 'Invalid fields and values data'}), 400

        # Update the specified fields for the user in Firebase
        for field, new_value in fields_and_values.items():
            update_user_field(user_id, field, new_value)

        return jsonify({'status': 'success', 'message': 'Fields updated successfully'}), 200

    except Exception as e:
        error_message = str(e)
        return jsonify({'status': 'error', 'message': error_message}), 500
    

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
    #refresh_token = token_data.get("refresh_token")  # Get the refresh token

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
        generate_token(user_info["id"], "refresh",expiration_refresh),
        httponly=True,
        secure=True,
        domain=f"{app.config['BACKEND_URL']}",
        path='/',
        samesite=None,
        expires=expiration_refresh,  # Set the expiration time
    )
    response.set_cookie(
        "jwt_access_token",
        generate_token(user_info["id"], "access",expiration_access),
        httponly=True,
        secure=True,
        domain=f"{app.config['BACKEND_URL']}",
        path='/',
        samesite=None,
        expires=expiration_access,  # Set the expiration time
    )
    return response



@app.route('/auth/logout', methods=['GET'])
@authenticate_and_get_user_data
def auth_logout(user_id):
    
    response = jsonify({'message': 'Logged out'})

    response.delete_cookie('jwt_refresh_token', path='/', domain=f"{app.config['BACKEND_URL']}", secure=True, samesite=None, httponly=True)
    response.delete_cookie('jwt_access_token', path='/', domain=f"{app.config['BACKEND_URL']}", secure=True, samesite=None, httponly=True)

    return response, 200


@app.route('/auth/verify-token', methods=['GET'])
@authenticate_and_get_user_data
def auth_verify_token(user_id):
    # Access token is valid, fetch user data from Firebase
    user_data = get_user_data_from_firebase(user_id)

    return jsonify({'message': 'Access token valid', 'user_data': user_data}), 200


@app.route('/valid_tickers', methods=['GET'])
@authenticate_and_get_user_data
def get_valid_tickers(user_id):
    try:
        valid_tickers = [
            { 'ticker': "DANSKE.CO", 'price': 2 },
            { 'ticker': "DEMANT.CO", 'price': 3 },
            { 'ticker': "DSV.CO", 'price': 4 }
        ]
        
        response_data = {
            'status': 'success',
            'data': valid_tickers,
            'user_id': user_id  # Including user_id in the response
        }
        
        return jsonify(response_data), 200  # 200 OK status code for successful response
    
    except Exception as e:
        error_message = str(e)
        response_data = {
            'status': 'error',
            'message': error_message
        }
        
        return jsonify(response_data), 500  # 500 Internal Server Error status code for errors



@app.route("/crunch_data", methods=["POST"])
@authenticate_and_get_user_data
def crunch_data(user_id):
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
        return jsonify(response_data), 200

    except Exception as e:
        # Handle any errors that may occur during data processing
        traceback_info = traceback.format_exc()  # Get the traceback as a string
        error_message = str(e)
        return jsonify({"error": error_message, "traceback": traceback_info}), 500


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=5000)
