import json
import uuid
from collections import defaultdict
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from datetime import date as dt_date
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field, field_validator, RootModel

class TickerRequest(BaseModel):
    tickers: List[str] = Field(..., description="List of tickers to fetch data for", example=["NOVO-B.CO", "BAVA.CO"])
    startDate: str = Field(..., description="Start date in YYYY-MM-DD format", example="2024-06-26")
    endDate: str = Field(..., description="End date in YYYY-MM-DD format", example="2024-07-26")

class Ticker(BaseModel):
    symbol: str = Field(..., description="The official ticker symbol")
    date: dt_date = Field(..., description="The date for this data")
    adj_close: float = Field(..., description="The adjusted closing price for this ticker on this day")

class DailyData(BaseModel):
    """
    Class representing daily data.
    """
    date: dt_date = Field(..., description="The date for this data")
    adj_close: float = Field(..., description="The adjusted close price for this day")

class Series(BaseModel):
    data: Dict[str, Dict[str, float]] = Field(..., description="The name of the time series")

    @property
    def df(self) -> pd.DataFrame:
        """
        Convert the series dictionary to a pandas DataFrame.
        """
        return pd.DataFrame(self.data) 
    
    @property
    def variance(self) -> float:
        """
        Calculate the variance of the returns.
        """
        return self.df.values.var()

    @property
    def mean(self) -> float:
        """
        Calculate the mean of the returns.
        """
        return self.df.values.mean()

class TimeSeries(BaseModel):
    """
    Class representing a time series for a stock.
    """
    prices: Optional[Series] = Field(None, description="The time series for the price history")
    returns: Optional[Series] = Field(None, description="The corresponding timeseries for the returns")
    future_prices: Optional[Series] = Field(None, description="The future prediction of the prices")
    future_returns: Optional[Series] = Field(None, description="The future prediction of the returns ")

    def __init__(self, **data):
        super().__init__(**data)
        self.returns = self.series_returns() if self.returns is None else self.returns

    def series_returns(self) -> pd.Series:
        """
        Calculate the returns using the pandas pct_change() method.
        """
        price_df = self.prices.df
        returns_df = price_df.pct_change().dropna()
        return Series(data=returns_df.to_dict(orient='dict'))


class TimeSeriesCollection(BaseModel):
    """
    Class representing a collection of time series for stocks.
    """
    collection: List[TimeSeries] = Field(..., description="A collection of time series")

    #def all_returns(self) -> List[float]:
    #    return np.concatenate([serie.returns.mean().values for serie in self.collection])

    def variances(self) -> List[float]:
        return [serie.returns.variance for serie in self.collection]

    def all_returns(self) -> List[float]:
        #return [serie.returns.mean().values for serie in self.collection]
        return [serie.returns.mean for serie in self.collection]

    def merge_dataframes(self) -> pd.DataFrame:
        """
        Combine each stock's returns into a DataFrame.
        """
        dataframes = []
        for timeserie in self.collection:
            dataframes.append(timeserie.returns.df)
        combined_df = pd.concat(dataframes, axis=1)
        return combined_df

    def covariance(self) -> pd.DataFrame:
        """
        Calculate the covariance matrix of returns.
        """
        returns_df = self.merge_dataframes()
        return returns_df.cov()

class Asset(BaseModel):
    """
    Class representing a part of a collection of stocks.
    """
    stock: TimeSeries = Field(..., description="The time series of the stock")
    weight: float = Field(..., description="The weight of this asset in the portfolio")

class Portfolio(BaseModel):
    """
    Class representing a collection of assets.
    """
    assets: List[Asset] = Field(..., description="A list of assets held in the portfolio")
    timeserie: Optional[TimeSeries] = Field(None, description="The aggregated time series of the portfolio")

    def __init__(self, **data):
        super().__init__(**data)
        self.timeserie = self.calculate_timeserie()
        

    def calculate_timeserie(self) -> TimeSeries:
        """
        Calculate the weighted time series for each asset.
        """
        weighted_series = [asset.stock.returns.df * asset.weight for asset in self.assets]
        merged_series = pd.concat(weighted_series, axis=1).sum(axis=1)
        df_with_header = pd.DataFrame(merged_series, columns=['weighted_timeseries'])
        timeserie_dict = df_with_header.to_dict()
        return TimeSeries(returns=Series(data=timeserie_dict))

    def calculate_expected_return(self) -> float:
        """
        Calculate the expected return of the portfolio.
        """
        return self.timeserie.returns.mean

    def calculate_variance(self) -> float:
        """
        Calculate the variance of the portfolio.
        """
        return self.timeserie.returns.variance
    
    def calculate_standard_deviation(self, variance)-> float:
        """
        Standard deviation
        """
        return variance ** 0.5

    def calculate_sharpe_ratio(self, expected_return, standard_deviation, risk_free_rate: float = 0.0) -> float:
        """
        Calculate the Sharpe ratio of the portfolio.
        """
        return (expected_return - risk_free_rate) / max(standard_deviation, 1e-12)

class PortfolioAnalysis(BaseModel):
    """
    Class representing the analysis of a portfolio.
    """
    #portfolio: Portfolio = Field(..., description="The portfolio being analyzed")
    sharpe_ratio: float = Field(..., description="The Sharpe ratio of the portfolio")
    expected_return: float = Field(..., description="The expected return of the portfolio")
    variance: float = Field(..., description="The portfolio's variance")
    standard_deviation: float = Field(None, description="The standard deviation of the portfolio")
    weights: Dict[str, float] = Field(..., description="The weights of the portfolio")


class PortfolioCollectionAnalysis(BaseModel):
    """
    Class representing the analysis of a collection of portfolios.
    """
    analysis: List[PortfolioAnalysis] = Field(..., description="Detailed analysis for each portfolio")

class PortfolioCollection(BaseModel):
    """
    Class representing a set of portfolios.
    """
    portfolios: List[Portfolio] = Field(..., description="A collection of portfolios")

    def analyze_portfolios(self, risk_free_rate: float = 0.0) -> PortfolioCollectionAnalysis:
        analysis = []

        for portfolio in self.portfolios:
            expected_return = portfolio.calculate_expected_return()
            variance = portfolio.calculate_variance()
            standard_deviation = portfolio.calculate_standard_deviation(variance=variance)
            sharpe_ratio = portfolio.calculate_sharpe_ratio(
                expected_return=expected_return,
                standard_deviation=standard_deviation,
                risk_free_rate=risk_free_rate)
            analysis.append(PortfolioAnalysis(
                #portfolio=portfolio,
                expected_return=expected_return,
                variance=variance,
                standard_deviation=standard_deviation,
                sharpe_ratio=sharpe_ratio,
                weights = {key: asset.weight for asset in portfolio.assets for key in asset.stock.returns.data.keys()}
            )
            )
        return PortfolioCollectionAnalysis(
            collection=self.portfolios,
            analysis=analysis
        )
    
class CombinedAnalysis(BaseModel):
    """
    Class representing the combined analysis of various portfolio strategies.
    """
    efficient_frontier: Optional[PortfolioCollectionAnalysis] = Field(None, description="Analysis of portfolios optimized for the efficient frontier")
    minimum_variance: Optional[PortfolioCollectionAnalysis] = Field(None, description="Analysis of portfolios optimized for minimum variance")
    maximum_sharpe: Optional[PortfolioCollectionAnalysis] = Field(None, description="Analysis of portfolios optimized for maximum Sharpe ratio")
    maximum_return: Optional[PortfolioCollectionAnalysis] = Field(None, description="Analysis of portfolios optimized for maximum return")
    random_weights: Optional[PortfolioCollectionAnalysis] = Field(None, description="Analysis of portfolios with randomly assigned weights")
    personal_weights: Optional[PortfolioCollectionAnalysis] = Field(None, description="Analysis of portfolios with personal weights")

class RequestAnalysis(BaseModel):
    """
    Class representing a request for portfolio analysis.
    """
    from_date: str = Field(..., description="Start date in YYYY-MM-DD format", example="2024-06-26")
    to_date: Optional[str] = Field(None, description="End date in YYYY-MM-DD format (optional, default is today)", example="2024-07-26")
    tickers: Dict[str, Dict[str, float]] = Field(..., description="Dictionary of tickers to fetch data for, with optional weights", example={"NOVO-B.CO": {'adj_close': 0.8, 'amount': 2}, "BAVA.CO": {'adj_close': 0.2, 'amount': 4}})
    risk_free_rate: Optional[float] = Field(0.0, description="Risk-free rate (default is 0)")

    @field_validator('from_date', 'to_date')
    def validate_date_format(cls, value):
        try:
            dt_date.fromisoformat(value)
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
        return value
    
class ResponseModel(BaseModel):
    request: RequestAnalysis = Field(..., description="The original request")
    plot_effecient_frontier: CombinedAnalysis = Field(..., description="The data for the plot for the effecient frontier")
    plot_prices: TimeSeriesCollection = Field(..., description="The data for the plot of the prices for all the tickers")

    