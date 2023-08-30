import os
from waitress import serve
import pathlib
from flask import Flask
import datetime as dt
from dateutil.relativedelta import relativedelta
from components.fetch_data_component import Common
import logging
from config import get_config

logger = logging.getLogger("waitress")
logger.setLevel(logging.INFO)
from flask_cors import CORS

# Read the value of the ENV_NODE environment variable
env_node = os.environ.get('ENV_NODE', 'development')  # Default to development
env_node = 'production'
# Get the selected configuration based on the environment node
selected_config = get_config(env_node)

app = Flask(__name__)
app.config.from_object(selected_config)

CORS(
    app,
    supports_credentials=True,
    resources={
        r"/crunch_data": {
            "origins": [f"{app.config['FRONTEND_PROTOCOL']}://{app.config['FRONTEND_URL']}"]
        },
        r"/valid_tickers": {
            "origins": [f"{app.config['FRONTEND_PROTOCOL']}://{app.config['FRONTEND_URL']}"]
        },
        r"/auth/verify-token": {
            "origins": [f"{app.config['FRONTEND_PROTOCOL']}://{app.config['FRONTEND_URL']}"]
        },
        r"/auth/logout": {
            "origins": [f"{app.config['FRONTEND_PROTOCOL']}://{app.config['FRONTEND_URL']}"]
        },
        r"/account/updateFields": {
            "origins": [f"{app.config['FRONTEND_PROTOCOL']}://{app.config['FRONTEND_URL']}"]
        },
        r"/account/delete": {
            "origins": [f"{app.config['FRONTEND_PROTOCOL']}://{app.config['FRONTEND_URL']}"]
        },
    },
)


# set variables
app.year = dt.datetime.now().year
app.today = dt.date.today()
app.yesterday = app.today - relativedelta(days=1)
app.last_year = app.today - relativedelta(years=1)

app.tickers_c20 = [
    # "MAERSK-A.CO",
    # "MAERSK-B.CO",
    # "AMBU-B.CO",
    # "BAVA.CO",
    # "CARL-B.CO",
    # "CHR.CO",
    # "COLO-B.CO",
    "DANSKE.CO",
    "DEMANT.CO",
    "DSV.CO",
    # "GMAB.CO",
    # "GN.CO",
    # "JYSK.CO",
    # "NOVO-B.CO",
    # "NZYM-B.CO",
    # "PNDORA.CO",
    # "RBREW.CO",
    # "TRYG.CO",
    # "VWS.CO",
    # "ORSTED.CO",
]
app.tickers_others = [
    "AAB.CO",
    # "AAK.ST",
    # "AGAT.CO",
    # "AGF-B.CO",
    # "ALK-B.CO",
    # "ALMB.CO",
    # "AQP.CO",
    # "ATLA-DKK.CO",
    # "BO.CO",
    # "BIOPOR.CO",
    # "BOOZT-DKK.CO",
    # "KLEE-B.CO",
    # "AOJ-B.CO",
    # "HART.CO",
    # "BIF.CO",
    # "CARL-A.CO",
    # "CHEMM.CO",
    # "CBRAIN.CO",
    # "CEMAT.CO",
    # "COLUM.CO",
    # "DNORD.CO",
    # "DAB.CO",
    # "DANT.CO",
    # "DFDS.CO",
    # "DJUR.CO",
    # "EAC.CO",
    # "ESG.CO",
    # "FED.CO",
    # "FFARMS.CO",
    # "FLS.CO",
    # "FLUG-B.CO",
    # "FYNBK.CO",
    # "GABR.CO",
    # "GERHSP.CO",
    # "GJ.CO",
    # "GREENH.CO",
    # "GREENM.CO",
    # "GRLA.CO",
    # "GYLD-A.CO",
    # "GYLD-B.CO",
    # "HLUN-A.CO",
    # "HLUN-B.CO",
    # "HH.CO",
    # "HARB-B.CO",
    # "HUSCO.CO",
    # "HVID.CO",
    # "IMAIL.CO",
    # "ISS.CO",
    # "JDAN.CO",
    # "KRE.CO",
    # "KBHL.CO",
    # "LOLB.CO",
    # "LUXOR-B.CO",
    # "LASP.CO",
    # "MATAS.CO",
    # "MTHH.CO",
    # "MNBA.CO",
    # "NETC.CO",
    # "NEWCAP.CO",
    # "NLFSK.CO",
    # "NKT.CO",
    # "NNIT.CO",
    # "NOBLE.CO",
    # "NDA-DK.CO",
    # "NRDF.CO",
    # "NORDIC.CO",
    # "NORTHM.CO",
    # "NTG.CO",
    # "NTR-B.CO",
    # "ORPHA.CO",
    # "PARKST-A.CO",
    # "PARKEN.CO",
    # "PENNEO.CO",
    # "PAAL-B.CO",
    # "PRIMOF.CO",
    # "RIAS-B.CO",
    # "RILBA.CO",
    # "RBLN-B.CO",
    # "ROCK-A.CO",
    # "ROCK-B.CO",
    # "ROV.CO",
    # "RTX.CO",
    # "SAS-DKK.CO",
    # "SBS.CO",
    # "STG.CO",
    # "SCHO.CO",
    # "SIF.CO",
    # "SIM.CO",
    # "SKAKO.CO",
    # "SKJE.CO",
    # "SOLAR-B.CO",
    # "SPG.CO",
    # "SPNO.CO",
    # "SPKSJF.CO",
    # "STRINV.CO",
    # "SYDB.CO",
    # "TCM.CO",
    # "TIV.CO",
    # "TOP.CO",
    # "TRMD-A.CO",
    # "TOTA.CO",
    # "TRIFOR.CO",
    # "UIE.CO",
    # "VJBA.CO",
    # "ZEAL.CO",
    # "OSSR.CO",
    # "CONFRZ.CO",
    # "MAPS.CO",
    # "GOOGL",
    # "AMZN",
    # "MSFT",
    # "TSLA",
    # "META",
    # "^DJI",
    # "^OMXC20",
]
app.tickers_dji = [
    "AXP",
    # "AMGN",
    # "AAPL",
    # "BA",
    # "CAT",
    # "CSCO",
    # "CVX",
    # "GS",
    # "HD",
    # "HON",
    # "IBM",
    # "INTC",
    # "JNJ",
    # "KO",
    # "JPM",
    # "MCD",
    # "MMM",
    # "MRK",
    # "MSFT",
    # "NKE",
    # "PG",
    # "TRV",
    # "UNH",
    # "CRM",
    # "VZ",
    # "V",
    # "WBA",
    # "WMT",
    # "DIS",
    # "DOW",
]
app.available_tickers = Common().union_lists(
    app.tickers_c20, app.tickers_others, app.tickers_dji
)

app.available_tickers_json = [
    {"value": ticker, "weight": "0"} for ticker in app.available_tickers
]


# Import the routes from the routes.py file
from routes import *


if __name__ == "__main__":
    # app.run(debug=True)
    # app.run(host='0.0.0.0', port=5000, debug=True)
    serve(app, host=app.config['HOST'], port=app.config['PORT'])

