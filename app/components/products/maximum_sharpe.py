from typing import Dict
from data.models import Portfolio, PortfolioCollection, Asset, TimeSeriesCollection
from components.producers import FetchData
from components.features.maximize_sharpe import MaximizeSharpe

class MaximumSharpe:
    def __init__(self, timeseries: TimeSeriesCollection):
        self.timeseries = timeseries

    def optimize_portfolios(self) -> PortfolioCollection:
        portfolios = []
        status, weights = MaximizeSharpe(
            returns=self.timeseries.all_returns(),
            cov_matrix=self.timeseries.covariance().values,
        ).optimize()

        if status:
            portfolios.append(Portfolio(
                assets=[Asset(stock=stock, weight=weights[i]) for i, stock in enumerate(self.timeseries.collection)]
            ))
                
        return PortfolioCollection(portfolios=portfolios)


