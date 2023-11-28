import numpy as np


class ploteffecientFrontier:
    def __init__(self, portfolios_data, analysis, comparison=None):
        # Prepare data
        self.data = self.crunch(portfolios_data, analysis, comparison)

    def format_portfolio_data(self, series_name, portfolios):
        formatted_data_dict = {
            "seriesName": series_name,
            "connected": portfolios["connected"],
            "backgroundColor": portfolios["backgroundColor"],
            "borderColor": portfolios["borderColor"],
            "data": [
                {
                    "x": portfolio["volatility"],
                    "y": portfolio["expected_return"],
                    "c": portfolio["sharpe_ratio"],
                    "tooltip": portfolio["tooltip"],
                }
                for portfolio in portfolios["portfolios"]
            ],
        }
        return formatted_data_dict

    def crunch(self, portfolio_data, analysis, comparison):
        # Reorganize the computed properties so it's ready for plotting in the front-end
        formatted_data = []
        for series_name, portfolios in portfolio_data.items():
            formatted_data.append(self.format_portfolio_data(series_name, portfolios))

        return formatted_data
