import datetime as dt
import yfinance as yf
import numpy as np
from scipy.optimize import minimize
import pandas as pd
import random
from flask import request, current_app
import json
from flask import url_for
import itertools
from dateutil.relativedelta import relativedelta


# class InfoFetcher:
# def __init__(self, tickers):
# self.tickers = tickers
# tickers_data = [Ticker(ticker) for ticker in tickers]
# self.info = [ticker.summary_detail for ticker in tickers_data]


class DataFetcher:
    def __init__(self, tickers, info, start=dt.datetime.today()-relativedelta(years=1)):
        self.tickers = tickers
        # self.currencies = {k: v["currency"] for item in info for k, v in item.items()}
        self.prices = self.get_data(self.tickers, info, start=start)
        self.returns = (self.prices - self.prices.shift(1)) / self.prices.shift(1) * 100

    def get_data(self, tickers, info, start):
        start_day = start  # dt.datetime.today()-relativedelta(years=1)
        end_day = current_app.today  # dt.datetime.today()
        # Find unique currencies
        # unique_currencies = []
        # for item in info:
        #    for value in item.values():
        #        currency = value['currency']
        #        if currency not in unique_currencies and currency not in 'DKK':
        #            unique_currencies.append(currency)
        # tickers_rates = [f'{currency}DKK=X' for currency in unique_currencies]  # List of Yahoo Finance ticker symbols

        # Find exchange rates
        # exchange_rates = yf.download(tickers=tickers_rates, period='1d')[
        #    "Adj Close"
        # ].tail(1)
        # if isinstance(exchange_rates, pd.Series):
        #    exchange_rates = exchange_rates.to_frame().rename(columns={'Adj Close': tickers_rates[0]})
        # exchange_rates["DKKDKK=X"] = 1
        # exchange_rates = exchange_rates.squeeze().to_dict()

        # Find stock prices
        data = yf.download(tickers, start=start_day, end=end_day)[
            "Adj Close"
        ]  # .tz_convert("CET")
        data = data[tickers]

        # Resample the data to a daily frequency
        data_daily = data.resample("D").last()

        # Fill in any missing values using forward-fill (i.e. fill with the last valid value)
        data_daily = data_daily.ffill()

        # Filter out rows corresponding to weekends
        weekday_mask = data_daily.index.weekday < 5
        data_weekdays = data_daily[weekday_mask]

        # exchangerate = []
        # for ticker in data_weekdays.columns:
        #    currency = self.currencies[ticker]
        #    exchangerate.append(exchange_rates[f'{currency}DKK=X'])

        data_weekdays = data_weekdays  # * exchangerate
        return data_weekdays


class Fetcher:
    def __init__(self, app,):
        # fetch data if not already exist
        if not hasattr(current_app, "last_data_retrival"):
            current_app.last_data_retrival = dt.date.today() - relativedelta(days=1)

        days_since_last_retrival = current_app.last_data_retrival - dt.date.today()

        # if not hasattr(current_app, "info") or days_since_last_retrival > dt.timedelta(
        #    days=1
        # ):
        #    current_app.info = InfoFetcher(app.available_tickers)

        if not hasattr(current_app, "data") or days_since_last_retrival > dt.timedelta(
            days=1
        ):
            current_app.data = DataFetcher(app.available_tickers, None)
            current_app.last_data_retrival = dt.date.today()


class Common:
    def __init__(self):
        pass

    def swap_columns(self, df, col1, col2):
        col_list = list(df.columns)
        x, y = col_list.index(col1), col_list.index(col2)
        col_list[y], col_list[x] = col_list[x], col_list[y]
        df = df[col_list]
        return df

    def union_lists(self, *lists):
        # use the chain() function from itertools to concatenate all the lists
        concatenated_list = list(itertools.chain(*lists))

        # use the set() function to remove duplicates and convert the concatenated list to a set
        unique_set = set(concatenated_list)

        # convert the set back to a list and return it as the final union
        final_union = list(unique_set)
        return final_union

    def core_return(self, returns, extrapolate):
        return returns.mean() * extrapolate

    def core_variance(self, returns, extrapolate):
        return returns.var() * extrapolate

    def core_standard_deviation(self, returns, extrapolate):
        return returns.std() * np.sqrt(extrapolate)

    def append_to_df(self, df, data, lookback, extrapolate, tickers):
        # Only take ticker columns of total data
        prices = data.prices[tickers]
        returns = data.returns[tickers]

        # Reorder
        returns = returns[df.index]
        prices = prices[df.index]

        # Compute rolling covariances
        rolling_cov = returns.rolling(lookback).cov()
        rolling_cov = rolling_cov.tail(len(rolling_cov.columns) * lookback)
        returns = returns.tail(lookback)
        prices = prices.tail(lookback)

        # Find returns, expected returns and variances
        expected_return = self.core_return(returns, extrapolate)
        variance = self.core_variance(returns, extrapolate)
        standard_deviation = self.core_standard_deviation(returns, extrapolate)

        # Find newest rows (cannot use date) this works even for holidays
        newest_idx = rolling_cov.index.levels[0].max()
        cov = rolling_cov.loc[newest_idx]

        cov = cov * extrapolate
        cov = cov.reindex(df.index)
        cov = cov[df.index]

        # merge the series onto the dataframe based on the 'ticker' column
        df = pd.merge(
            df,
            expected_return.rename("expected_return"),
            left_on="ticker",
            right_index=True,
        )

        # Add the variances for each of the signals to the df
        df = pd.merge(
            df, variance.rename("variance"), left_on="ticker", right_index=True
        )

        # Add the variances for each of the signals to the df
        df = pd.merge(
            df,
            standard_deviation.rename("standard_deviation"),
            left_on="ticker",
            right_index=True,
        )

        return {
            "df": df,
            "prices": prices,
            "returns": returns,
            "cov": cov,
            "rolling_cov": rolling_cov,
        }


class html:
    def __init__(self):
        pass

    def dataframe_to_html(df):
        # Format all values in the DataFrame with two significant digits
        df = df.applymap(lambda x: f"{x:.4g}")

        table_html = "<table><thead><tr><th></th>"

        # add column headers
        for col in df.columns:
            table_html += f"<th>{col}</th>"
        table_html += "</tr></thead><tbody>"

        # add index and data rows
        for i, idx in enumerate(df.index):
            table_html += "<tr>"
            table_html += f"<td>{idx}</td>"
            for col in df.columns:
                table_html += f"<td>{df.iloc[i][col]}</td>"
            table_html += "</tr>"

        table_html += "</tbody></table>"
        return f"<div>{table_html}</div>"

    def portfolio_comparison(p1, p2):
        # subtract the two dataframes
        w1 = p1.portfolios[0].weights
        w2 = p2.portfolios[0].weights
        diff = w2 - w1
        df = diff.to_frame()

        # add column headers
        table_html = "<table><thead><tr><th></th>"
        table_html += f"<th>Difference (%)</th>"
        table_html += "</tr></thead><tbody>"

        # add index and data rows
        for i, idx in enumerate(df.index):
            table_html += "<tr>"
            table_html += f"<td>{idx}</td>"
            for col in df.columns:
                # table_html += f'<td>{df.iloc[i][col]}</td>'
                if df.iloc[i][col] > 0:
                    action = "buy"
                elif df.iloc[i][col] < 0:
                    action = "sell"
                else:
                    action = "hold"
                table_html += f"<td>{action} {np.abs(df.iloc[i][col]):.4g}%</td>"
            table_html += "</tr>"
        table_html += "</tbody></table>"
        return f"<div>{table_html}</div>"


class Financial:
    def __init__(self):
        pass

    def portfolio_return(self, returns, weights):
        return np.sum(returns * weights)

    def portfolio_volatility(self, weights, cov_matrix):
        # Calculate the vector-matrix-vector product
        return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

    def sharpe_ratio_scalar(self, expected_return, volatility, rf=0.0):
        if (expected_return == 0) & (volatility == 0):
            return 0
        return (expected_return - rf) / volatility

    def sharpe_ratio(self, returns, weights, cov_matrix, rf=0.0):
        expected_return = self.portfolio_return(returns, weights)
        volatility = self.portfolio_volatility(weights, cov_matrix)
        return self.sharpe_ratio_scalar(expected_return, volatility, rf)

    def random_portfolios(n, m):
        random_portfolios = []

        for _ in range(n):
            portfolio = []

            # Generate m random values between 0 and 1
            for _ in range(m):
                value = random.uniform(0, 1)
                portfolio.append(value)

            # Normalize the portfolio
            total = sum(portfolio)
            normalized_portfolio = [value / total for value in portfolio]

            random_portfolios.append(normalized_portfolio)
        return random_portfolios

    def all_in_one_portfolios(n):
        lists = []
        for i in range(n):
            sublist = [0] * n
            sublist[i] = 1
            lists.append(sublist)
        return lists

    def reconstruct_covariance_matrix(self, df):
        # Get unique tickers
        tickers = df[["ticker1", "ticker2"]].stack().unique()

        # Initialize full covariance matrix as a dataframe
        cov_matrix = pd.DataFrame(index=tickers, columns=tickers)

        variances = df.query("ticker1==ticker2")
        covariances1 = df.query("ticker1!=ticker2")
        covariances2 = Common().swap_columns(
            covariances1.rename(columns={"ticker1": "ticker2", "ticker2": "ticker1"}),
            "ticker1",
            "ticker2",
        )

        # elements for the covariances matrix
        elements = pd.concat(
            [variances, covariances1, covariances2], ignore_index=True, axis=0
        )

        # Fill lower triangle of covariance matrix with covariance values
        for i, row in elements.iterrows():
            cov_matrix.at[row["ticker1"], row["ticker2"]] = row["covariance"]

        # Return covariance matric
        return cov_matrix

    def create_portfolio(
        df,
        cov_matrix,
        constructor=None,
        mode=None,
        name=None,
        constrains=[None],
        connected=False,
        backgroundColor=False,
        borderColor=False,
    ):
        portfolios = []
        for constrain in constrains:
            portfolio_df = df.copy()
            if constructor is not None:
                portfolio_df["ratio"] = constructor(
                    df["expected_return"],
                    cov_matrix=cov_matrix,
                    constrain=constrain,
                    mode=mode,
                ).optimize()
            portfolios.append(Portfolio(portfolio_df, cov_matrix=cov_matrix))
        return Portfolios(
            portfolios,
            name=name,
            connected=connected,
            backgroundColor=backgroundColor,
            borderColor=borderColor,
        ).data


class Portfolio:
    def __init__(self, portfolio_df, cov_matrix, risk_free_rate=0.0):
        self.tickers = portfolio_df.index
        self.weights = portfolio_df["ratio"]
        self.risk_free_rate = risk_free_rate
        self.expected_return = Financial().portfolio_return(
            portfolio_df["expected_return"], self.weights
        )
        self.volatility = Financial().portfolio_volatility(
            self.weights, cov_matrix=cov_matrix
        )
        self.sharpe_ratio = Financial().sharpe_ratio_scalar(
            self.expected_return, self.volatility, risk_free_rate
        )
        # Initialize tooltip with the common part
        self.tooltip = f"""Mean return: {self.expected_return:.2}%\n
        Standard deviation: {self.volatility:.2}%\n
        Sharpe-ratio: {self.sharpe_ratio:.2f}\n"""

        # Check if any weight is larger than 0
        if any(weight > 0 for weight in self.weights):
            self.tooltip += f"""Weights:\n"""
            # Iterate through tickers and weights, and add to the tooltip if weight > 0
            for ticker, weight in zip(self.tickers, self.weights):
                if weight > 0:
                    self.tooltip += f"""{ticker}: {weight:.2%}\n"""

        self.data = {
            "expected_return": self.expected_return,  # y
            "volatility": self.volatility,  # x
            "tooltip": self.tooltip,  # tooltip
            "sharpe_ratio": self.sharpe_ratio,  # for coluring/scaling/rating
        }


class Portfolios:
    def __init__(
        self,
        portfolios,
        name=None,
        connected=False,
        backgroundColor=False,
        borderColor=False,
    ):
        self.portfolios = [portfolio.data for portfolio in portfolios]
        # self.expected_returns = [portfolio.expected_return for portfolio in portfolios]
        # self.volatilities = [portfolio.volatility for portfolio in portfolios]
        # self.sharpe_ratios = [portfolio.sharpe_ratio for portfolio in portfolios]
        self.name = name
        self.data = {
            "tickers": portfolios[0].tickers.tolist(),
            "risk_free_rate": portfolios[0].risk_free_rate,
            "portfolios": self.portfolios,
            "connected": connected,
            "backgroundColor": backgroundColor,
            "borderColor": borderColor,
        }
        #            'expected_returns': self.expected_returns,
        #            'volatilities': self.volatilities,
        #            'sharpe_ratios': self.sharpe_ratios,
        #'name': self.name
        # }


class Sharpe:
    def __init__(
        self, returns, cov_matrix=None, constrain=None, counter=None, mode=None
    ):
        self.returns = returns
        self.cov_matrix = cov_matrix
        self.mode = mode
        self.weights = self.optimize()

    def optimize(self):
        n = len(self.returns)
        bounds = [(0, 1) for i in range(n)]
        constraints = {"type": "eq", "fun": lambda x: np.sum(x) - 1}
        initial_guess = np.array([1 / n for i in range(n)])
        result = minimize(
            lambda x: -Financial().sharpe_ratio(
                self.returns, x, self.cov_matrix, rf=0.0
            ),
            initial_guess,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
        )
        weights = pd.DataFrame(
            data=result.x, index=self.returns.index, columns=["weights"]
        )
        return weights


class Settings:
    def __init__(self):
        self.tickers = self.read_tickers("tickers")
        self.benchmarks = self.read_tickers("benchmarks")
        self.extrapolate = self.read_extrapolate()
        self.lookback = self.read_lookback()
        self.rfr = self.read_rfr()
        if self.benchmarks is not None:
            self.url_index = url_for(
                "home",
                tickers=request.args.get("tickers"),
                benchmarks=request.args.get("benchmarks"),
                lookback=request.args.get("lookback"),
                extrapolate=request.args.get("extrapolate"),
                rfr=request.args.get("rfr"),
            )
            self.url_crunch = url_for(
                "crunch_data",
                tickers=request.args.get("tickers"),
                benchmarks=request.args.get("benchmarks"),
                lookback=request.args.get("lookback"),
                extrapolate=request.args.get("extrapolate"),
                rfr=request.args.get("rfr"),
            )
        else:
            self.url_index = url_for(
                "home",
                tickers=request.args.get("tickers"),
                lookback=request.args.get("lookback"),
                extrapolate=request.args.get("extrapolate"),
                rfr=request.args.get("rfr"),
            )
            self.url_crunch = url_for(
                "crunch_data",
                tickers=request.args.get("tickers"),
                lookback=request.args.get("lookback"),
                extrapolate=request.args.get("extrapolate"),
                rfr=request.args.get("rfr"),
            )

        if self.tickers is not None:
            self.analysis = pd.DataFrame(
                {
                    "ticker": [ticker[0] for ticker in self.tickers],
                    "ratio": [ticker[1] for ticker in self.tickers],
                }
            ).set_index(["ticker"])
        else:
            self.analysis = None
        if self.benchmarks is not None:
            self.comparison = pd.DataFrame(
                {
                    "ticker": [benchmark[0] for benchmark in self.benchmarks],
                    "ratio": [benchmark[1] for benchmark in self.benchmarks],
                }
            ).set_index(["ticker"])
        else:
            self.comparison = None

    def read_tickers(self, string):
        # tickers_input = request.args.getlist("tickers")
        tickers_input = request.args.get(string)
        if tickers_input:
            tickers_dict = json.loads(tickers_input)
            # extract the ticker values into a list of strings
            tickers = [
                (ticker["value"], float(ticker["weight"])) for ticker in tickers_dict
            ]
        else:
            tickers = None
            # tickers = [
            # ("MAERSK-A.CO",0.00),
            # ("MAERSK-B.CO",0.00),
            # ("AMBU-B.CO",0.00),
            # ("BAVA.CO",0.00),
            # ("CARL-B.CO",0.00),
            # ("CHR.CO",0.00),
            # ("COLO-B.CO",0.00),
            # ("DANSKE.CO",0.00),
            # ("DEMANT.CO",0.00),
            # ("DSV.CO",0.00),
            # ("GMAB.CO",0.00),
            # ("GN.CO",0.00),
            # ("JYSK.CO",0.00),
            # ("NOVO-B.CO",0.00),
            # ("NZYM-B.CO",0.00),
            # ("PNDORA.CO",0.00),
            # ("RBREW.CO",0.00),
            # ("TRYG.CO",0.00),
            # ("VWS.CO",0.00),
            # ("ORSTED.CO",0.00),
            # ]
        return tickers

    def read_lookback(self):
        lookback = request.args.get("lookback")
        if lookback is not None:
            try:
                return int(lookback)
            except:
                print("lookback must be an integer")
        else:
            return 30

    def read_extrapolate(self):
        extrapolate = request.args.get("extrapolate")
        if extrapolate is not None:
            try:
                return int(extrapolate)
            except:
                print("extrapolate must be an integer")
        else:
            return 1

    def read_rfr(self):
        rfr = request.args.get("rfr")
        if rfr is not None:
            try:
                return float(rfr)
            except:
                print("rfr must be a floating point number")
        else:
            return 0


class PreWeighted:
    def __init__(self, returns, cov_matrix, constrain=None, counter=None, mode=None):
        self.returns = returns
        self.equilibrium_return = constrain
        self.cov_matrix = cov_matrix
        self.counter = counter
        self.weights = self.optimize()

    def optimize(self):
        return self.equilibrium_return


class VolatilityMinimizer:
    def __init__(self, returns, cov_matrix, constrain=None, counter=None, mode=None):
        self.returns = returns
        self.equilibrium_return = constrain
        self.cov_matrix = cov_matrix
        self.weights = self.optimize()

    def optimize(self):
        n = len(self.returns)
        bounds = [(0, 1) for i in range(n)]
        constraints = [{"type": "eq", "fun": lambda x: np.sum(x) - 1}]

        if self.equilibrium_return is not None:
            constraints.append(
                {
                    "type": "eq",
                    "fun": lambda x: Financial().portfolio_return(
                        self.returns, weights=x
                    )
                    - self.equilibrium_return,
                }
            )

        initial_guess = np.array([1 / n for i in range(n)])
        result = minimize(
            lambda x: Financial().portfolio_volatility(
                weights=x, cov_matrix=self.cov_matrix
            ),
            initial_guess,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
        )
        weights = pd.DataFrame(
            data=result.x, index=self.returns.index, columns=["weights"]
        )
        return weights


class app:
    def __init__(self):
        self.load_time = dt.datetime.now()
