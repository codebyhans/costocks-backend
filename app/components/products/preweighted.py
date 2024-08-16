from typing import Dict
from data.models import PortfolioCollection, TimeSeriesCollection, Asset, Portfolio
from components.features.assign_weights import AssignWeights
import numpy as np 

class Preweighted:
    def __init__(self, timeseries:TimeSeriesCollection):
        self.timeseries = timeseries 

    def _assign_weights(self, np_weights):
        portfolios = []
        for weights in np_weights:
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


    def optimize_portfolios(self, number_of_portfolios=100) -> PortfolioCollection:

        # Create 'number_of_portfolios' random portfolios using numpy. All weights must sum to one
        random_weights = []
        num_assets = len(self.timeseries.collection)
        random_weights = np.random.random((number_of_portfolios, num_assets))
        
        # Normalize the weights so that each row sums to one
        random_weights /= random_weights.sum(axis=1)[:, np.newaxis]

        return self._assign_weights(np_weights=random_weights)
        
    def assign_weights(self, tickers):

        values = np.array([ticker['adj_close'] * ticker['amount'] for ticker in tickers.values()])

        # Step 2: Calculate the total portfolio value
        total_value = np.sum(values)

        # Step 3: Calculate the weights of each ticker
        weights = [values / total_value]

        return self._assign_weights(np_weights=weights)

