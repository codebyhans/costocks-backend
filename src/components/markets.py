# from app import app
# from core.data_fetcher import DataFetcher
# from core.common import Common
# import core as c
# import pandas as pd
# from components.fetch_data_component import Financial
# from components.fetch_data_component import PreWeighted
# import datetime as dt
#
#
# class Markets:
#    def __init__(self, lookback, extrapolate, end_date=dt.date.today()):
#        while end_date.weekday() > 4:
#            end_date -= 1
#
#        self.lookback = lookback
#        self.end_date = end_date
#        self.extrapolate = extrapolate
#        self.markets = {
#            "MARKET-ID": market(
#                tickers=[ticker["value"] for ticker in app.available_tickers],
#                markets=self,
#            )
#        }
#
#
# class market:
#    def __init__(self, tickers, markets):
#        self.tickers = tickers
#
#        # Build dataframe for analysis
#        df_analysis = pd.DataFrame(
#            {
#                "ticker": [ticker for ticker in tickers],
#                "ratio": [1 for ticker in tickers],
#            }
#        ).set_index(["ticker"])
#
#        self.data_market = DataFetcher(self.tickers, markets.lookback, markets.end_date)
#
#        analysis = Common(app).append_to_df(
#            df=df_analysis,
#            data=self.data_market,
#            lookback=markets.lookback,
#            extrapolate=markets.extrapolate,
#        )
#
#        # Create portfolios for every stock
#        self.portfolios = Financial.create_portfolio(
#            df=analysis["df"],
#            cov_matrix=analysis["cov"],
#            constructor=PreWeighted,
#            constrains=Financial.all_in_one_portfolios(len(analysis["df"])),
#        )
