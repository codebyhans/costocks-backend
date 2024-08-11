from data.models import TimeSeries, TimeSeriesCollection, Ticker, Series, TickerRequest
from typing import List, Dict
from components.producers.worker import Worker
import os
from dotenv import load_dotenv

class Fetch: 
    def __init__(self):

        load_dotenv()
        self.DB_URI = os.getenv('DB_URI')
        self.DB_KEY = os.getenv('DB_PRIMARY_KEY')
        self.DATABASE_NAME = os.getenv('DATABASE_NAME')
        self.CONTAINER_NAME = os.getenv('CONTAINER_NAME')
        self.worker = Worker(DB_URI=self.DB_URI, DB_KEY=self.DB_KEY, DATABASE_NAME=self.DATABASE_NAME, CONTAINER_NAME=self.CONTAINER_NAME)

    def timeseries(self, tickers: List[str], from_date: str, to_date: str):
        request = TickerRequest(
            tickers=tickers,
            startDate=from_date,
            endDate=to_date
        )
        raw_timeseries = self.worker.timeseries(request=request)
        timeseries=[]
        for ticker in raw_timeseries.keys():
            timeseries_data = Series(data={ticker: raw_timeseries[ticker]})
            timeseries.append(TimeSeries(prices=timeseries_data)
            )
        return TimeSeriesCollection(collection=timeseries)
        
    def tickers(self):
        tickers_data = self.worker.tickers()
        return [Ticker(symbol=ticker.symbol, adj_close=ticker.adj_close, date=ticker.date) for ticker in tickers_data]