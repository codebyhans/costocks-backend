import requests 
from data.models import TimeSeries, TimeSeriesCollection
from typing import List, Dict
import pandas as pd

class FetchData:
    def __init__(self, tickers: List[str], from_date: str, to_date: str):
        self.tickers = tickers
        self.from_date = from_date
        self.to_date = to_date
        self.endpoint = "https://datafetcher.wittybeach-c0d983ae.northeurope.azurecontainerapps.io/deliver"  # Replace with the actual endpoint
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
            self.timeseries = TimeSeriesCollection(series=[
                TimeSeries(
                    name=ticker,
                    timeserie_dict=tickers[ticker]
                )
                for ticker in tickers.keys()
            ]
            )
        else:
            raise Exception(f"Failed to fetch data: {response.status_code}, {response.text}")