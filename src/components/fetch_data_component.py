import datetime as dt
from core.data_fetcher import DataFetcher
from flask import  current_app
from dateutil.relativedelta import relativedelta

class Fetcher:
    def __init__(self, app,):
        # fetch data if not already exist
        if not hasattr(current_app, "last_data_retrival"):
            current_app.last_data_retrival = dt.date.today() - relativedelta(days=1)

        days_since_last_retrival = current_app.last_data_retrival - dt.date.today()

        # if not hasattr(current_app, "info") or days_since_last_retrival > dt.timedelta(
        #    days=1
        # ):
        #    current_app.info = InfoFetcher(app.available_tickers)

        if not hasattr(current_app, "data") or days_since_last_retrival > dt.timedelta(
            days=1
        ):
            current_app.data = DataFetcher(app.available_tickers, None)
            current_app.last_data_retrival = dt.date.today()

class app:
    def __init__(self):
        self.load_time = dt.datetime.now()
