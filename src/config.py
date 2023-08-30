class Config:
    DEBUG = False  # Set to True to enable debugging mode
    PORT = 5000  # Set the port you want your app to run on
    HOST = '0.0.0.0'  # Set the host IP address
    BASE_URL = None
    # Define other configuration parameters here

    TICKERS_C20 = [
        # ... list of C20 tickers
    ]
    TICKERS_OTHERS = [
        # ... list of other tickers
    ]
    TICKERS_DJI = [
        # ... list of DJI tickers
    ]
    
class DevelopmentConfig(Config):
    DEBUG = True
    BASE_URL = 'localhost:9000'
    PROTOCOL = 'http'
class ProductionConfig(Config):
    DEBUG = False
    BASE_URL = 'qp-invest-frontend.web.app'
    PROTOCOL = 'https'

# Function to get the selected configuration based on env_node
def get_config(env_node):
    config_by_env_node = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
    }
    return config_by_env_node.get(env_node.lower(), DevelopmentConfig)