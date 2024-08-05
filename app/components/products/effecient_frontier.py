import numpy as np
from typing import Dict
from data.models import Portfolio, PortfolioCollection, Asset, TimeSeriesCollection
from components.features.minimize_volatility import MinimizerVolatility

class EfficientFrontier:
    def __init__(self, timeseries: TimeSeriesCollection):
        self.timeseries=timeseries

    def optimize_portfolios(self, number_of_portfolios=100) -> PortfolioCollection:
        portfolios = []

        min_returns = min(self.timeseries.all_returns()) + 10e-12
        max_returns = max(self.timeseries.all_returns())  - 10e-12

        for constrain in np.linspace(start=min_returns, stop=max_returns, num=number_of_portfolios):
            status, weights = MinimizerVolatility(
                returns=self.timeseries.all_returns(),
                cov_matrix=self.timeseries.covariance().values,
                constrain=constrain
            ).optimize()

            if status:
                portfolios.append(Portfolio(
                    assets=[Asset(stock=stock, weight=weights[i]) for i, stock in enumerate(self.timeseries.collection)]
                ))
                
        return PortfolioCollection(portfolios=portfolios)


