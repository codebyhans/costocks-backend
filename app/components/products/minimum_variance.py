from typing import Dict
from data.models import PortfolioCollection, TimeSeriesCollection, Asset, Portfolio
from components.producers import FetchData
from components.features.minimize_volatility import MinimizerVolatility

class MinimumVariance:
    def __init__(self, timeseries: TimeSeriesCollection):
        self.timeseries = timeseries

    def optimize_portfolios(self) -> PortfolioCollection:
        portfolios = []

        status, weights = MinimizerVolatility(
            returns=self.timeseries.all_returns(),
            cov_matrix=self.timeseries.covariance().values,
            ).optimize()

        if status:
            portfolios.append(Portfolio(
                assets=[Asset(stock=stock, weight=weights[i]) for i, stock in enumerate(self.timeseries.collection)]
            ))
                
        return PortfolioCollection(portfolios=portfolios)


