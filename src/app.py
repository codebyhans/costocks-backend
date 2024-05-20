import os
from waitress import serve
from flask import Flask
from dateutil.relativedelta import relativedelta

# from components.fetch_data_component import Common
import logging
from config import get_config

logger = logging.getLogger("waitress")
logger.setLevel(logging.INFO)
from flask_cors import CORS

# Read the value of the ENV_NODE environment variable
env_node = os.getenv("ENV_NODE", "development")  # Default to development

# Get the selected configuration based on the environment node
selected_config = get_config(env_node)

app = Flask(__name__)
app.config.from_object(selected_config)

CORS(
    app,
    supports_credentials=True,
    resources={
        r"/crunch_data": {
            "origins": [
                f"{app.config['FRONTEND_PROTOCOL']}{app.config['FRONTEND_URL']}{app.config['FRONTEND_PORT']}"
            ]
        },
        r"/portfolios": {
            "origins": [
                f"{app.config['FRONTEND_PROTOCOL']}{app.config['FRONTEND_URL']}{app.config['FRONTEND_PORT']}"
            ]
        },
        r"/valid_tickers": {
            "origins": [
                f"{app.config['FRONTEND_PROTOCOL']}{app.config['FRONTEND_URL']}{app.config['FRONTEND_PORT']}"
            ]
        },
        r"/auth/verify-token": {
            "origins": [
                f"{app.config['FRONTEND_PROTOCOL']}{app.config['FRONTEND_URL']}{app.config['FRONTEND_PORT']}"
            ]
        },
        r"/auth/logout": {
            "origins": [
                f"{app.config['FRONTEND_PROTOCOL']}{app.config['FRONTEND_URL']}{app.config['FRONTEND_PORT']}"
            ]
        },
        r"/account/updateFields": {
            "origins": [
                f"{app.config['FRONTEND_PROTOCOL']}{app.config['FRONTEND_URL']}{app.config['FRONTEND_PORT']}"
            ]
        },
        r"/account/delete": {
            "origins": [
                f"{app.config['FRONTEND_PROTOCOL']}{app.config['FRONTEND_URL']}{app.config['FRONTEND_PORT']}"
            ]
        },
    },
)

# Import the routes from the routes.py file
from routes import *

if __name__ == "__main__":
    serve(app, host=app.config["HOST"], port=app.config["PORT"])
