from typing import Dict
from data.models import PortfolioCollection, TimeSeriesCollection, Asset, Portfolio
from components.producers import FetchData
from components.features.assign_weights import AssignWeights
import numpy as np 

class Preweighted:
    def __init__(self, from_date: str, to_date: str, tickers: Dict[str, float]):
        self.from_date = from_date
        self.to_date = to_date
        self.tickers = tickers
        self.timeseries = self.fetch()

    def fetch(self) -> TimeSeriesCollection:
        # Fetch stock data using the FetchData class
        return FetchData(
            tickers=list(self.tickers.keys()),
            from_date=self.from_date,
            to_date=self.to_date,
        ).timeseries

    def optimize_portfolios(self, number_of_portfolios=100) -> PortfolioCollection:
        portfolios = []

        # Create 'number_of_portfolios' random portfolios using numpy. All weights must sum to one
        random_weights = []
        num_assets = len(self.timeseries.collection)

        random_weights = np.random.random((number_of_portfolios, num_assets))
    
        # Normalize the weights so that each row sums to one
        random_weights /= random_weights.sum(axis=1)[:, np.newaxis]

        for weights in random_weights:
            status, weights = AssignWeights(
                returns=self.timeseries.all_returns(),
                cov_matrix=self.timeseries.covariance().values,
                constrain=weights
            ).optimize()

            if status:
                portfolios.append(Portfolio(
                    assets=[Asset(stock=stock, weight=weights[i]) for i, stock in enumerate(self.timeseries.collection)]
                ))

        return PortfolioCollection(portfolios=portfolios)

