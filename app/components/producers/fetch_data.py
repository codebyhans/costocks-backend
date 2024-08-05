import requests 
from data.models import TimeSeries, TimeSeriesCollection, Ticker
from typing import List, Dict
import pandas as pd

class FetchData:
    def __init__(self, tickers: List[str], from_date: str, to_date: str):
        self.tickers = tickers
        self.from_date = from_date
        self.to_date = to_date
        self.endpoint = "https://datafetcher.wittybeach-c0d983ae.northeurope.azurecontainerapps.io/deliver"  # Replace with the actual endpoint
        self.timeseries = None
        self.fetcher = self.fetch_data()

    def fetch_data(self):
        payload = {
            "tickers": self.tickers,
            "startDate": self.from_date,
            "endDate": self.to_date
        }
        response = requests.post(self.endpoint, json=payload)
        if response.status_code == 200:
            tickers = response.json()
            timeseries=[]
            for ticker in tickers.keys():
                timeseries_data = {ticker: tickers[ticker]}
                timeseries.append(TimeSeries(series=timeseries_data)
                )

            self.timeseries = TimeSeriesCollection(collection=timeseries)

        else:
            raise Exception(f"Failed to fetch data: {response.status_code}, {response.text}")
        

class FetchTickers:
    def __init__(self):
        self.endpoint = "https://datafetcher.wittybeach-c0d983ae.northeurope.azurecontainerapps.io/distinct-tickers"
        self.ticker_collection = self.fetch_data()

    def fetch_data(self):
        response = requests.get(self.endpoint)
        if response.status_code == 200:
            tickers_data = response.json()  # Assuming response JSON is a list of ticker symbols
            ticker_collection = [Ticker(symbol=ticker['ticker'], adj_close=ticker['adj_close'], date=ticker['date']) for ticker in tickers_data]
            return ticker_collection
        else:
            raise Exception(f"Failed to fetch data: {response.status_code}, {response.text}")
