from typing import Dict
from data.models import PortfolioCollection, TimeSeriesCollection, Asset, Portfolio
from components.producers import FetchData
from components.features.minimize_volatility import MinimizerVolatility

class MinimumVariance:
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


