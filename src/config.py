import os
from dotenv import load_dotenv, find_dotenv


class Config:
    DEBUG = False  # Set to True to enable debugging mode
    PORT = 5000  # Set the port you want your app to run on
    HOST = "0.0.0.0"  # Set the host IP address

class DevelopmentConfig(Config):
    #Fetch .env files 
    load_dotenv(find_dotenv())


    PORT = 5000
    DEBUG = True
    FRONTEND_PROTOCOL = "http://"
    FRONTEND_URL = "localhost"
    FRONTEND_PORT = ":9000"

    BACKEND_PROTOCOL = "http://"
    BACKEND_URL = "localhost"
    BACKEND_PORT = ":5000"

    FIREBASE_TYPE = os.getenv("FIREBASE_TYPE").replace(r'\n', '\n')
    FIREBASE_PRIVATE_KEY = os.getenv("FIREBASE_PRIVATE_KEY").replace(r'\n', '\n')
    FIREBASE_CLIENT_EMAIL = os.getenv("FIREBASE_CLIENT_EMAIL").replace(r'\n', '\n')
    FIREBASE_CLIENT_ID = os.getenv("FIREBASE_CLIENT_ID").replace(r'\n', '\n')
    FIREBASE_TOKEN_URI = os.getenv("FIREBASE_TOKEN_URI").replace(r'\n', '\n')
    FIREBASE_DATABASE_URL = os.getenv("FIREBASE_DATABASE_URL").replace(r'\n', '\n')

    

class ProductionConfig(Config):
    PORT = 8080
    DEBUG = False
    FRONTEND_PROTOCOL = "https://"
    FRONTEND_URL = "costock.wittybeach-c0d983ae.northeurope.azurecontainerapps.io"
    FRONTEND_PORT = ""

    BACKEND_PROTOCOL = "https://"
    BACKEND_URL = "costocks-backend-a.internal.wittybeach-c0d983ae.northeurope.azurecontainerapps.io"
    BACKEND_PORT = ""

    FIREBASE_TYPE = os.getenv("FIREBASE_TYPE").replace(r'\n', '\n')
    FIREBASE_PRIVATE_KEY = os.getenv("FIREBASE_PRIVATE_KEY").replace(r'\n', '\n')
    FIREBASE_CLIENT_EMAIL = os.getenv("FIREBASE_CLIENT_EMAIL").replace(r'\n', '\n')
    FIREBASE_CLIENT_ID = os.getenv("FIREBASE_CLIENT_ID").replace(r'\n', '\n')
    FIREBASE_TOKEN_URI = os.getenv("FIREBASE_TOKEN_URI").replace(r'\n', '\n')
    FIREBASE_DATABASE_URL = os.getenv("FIREBASE_DATABASE_URL").replace(r'\n', '\n')




# Function to get the selected configuration based on env_node
def get_config(env_node="development"):
    config_by_env_node = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
    }
    return config_by_env_node.get(env_node.lower(), DevelopmentConfig)
