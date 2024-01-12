class Config:
    DEBUG = False  # Set to True to enable debugging mode
    PORT = 5000  # Set the port you want your app to run on
    HOST = "0.0.0.0"  # Set the host IP address
    FRONTEND_URL = None


class DevelopmentConfig(Config):
    DEBUG = True
    FRONTEND_PROTOCOL = "http://"
    FRONTEND_URL = "localhost"
    FRONTEND_PORT = ":9000"

    BACKEND_PROTOCOL = "http://"
    BACKEND_URL = "localhost"
    BACKEND_PORT = ":5000"


class ProductionConfig(Config):
    DEBUG = False
    FRONTEND_PROTOCOL = "https://"
    FRONTEND_URL = "qp-invest-frontend.web.app"
    FRONTEND_PORT = ""

    BACKEND_PROTOCOL = "https://"
    BACKEND_URL = "qpinvest-nbdj-main-i4enuayvva-lz.a.run.app"
    BACKEND_PORT = ""


# Function to get the selected configuration based on env_node
def get_config(env_node):
    config_by_env_node = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
    }
    return config_by_env_node.get(env_node.lower(), DevelopmentConfig)
