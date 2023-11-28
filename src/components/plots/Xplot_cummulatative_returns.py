import numpy as np


class plotCumulativeReturns:
    def __init__(self, portfolios_data, analysis, comparison=None):
        # Prepare data
        self.data = self.crunch(portfolios_data, analysis, comparison)

    def format_portfolio_data(self, series_name, portfolios, analysis):
        formatted_data_dict = {
            "seriesName": series_name,
            "connected": portfolios["connected"],
            "backgroundColor": portfolios["backgroundColor"],
            "borderColor": portfolios["borderColor"],
            "data": [],
        }

        for portfolio in portfolios["portfolios"]:
            # Assuming each portfolio is a DataFrame with ticker weights
            weights_df = portfolio["weights"]
            returns_df = analysis.returns

            # Calculate the portfolio returns
            result_series = returns_df.dot(weights_df["weights"].T)

            # Cumulatative returns
            cumulative_returns = (1 + result_series / 100).cumprod() - 1

            # Calculate the cumulative returns
            cumulative_returns = (1 + result_series / 100).cumprod() - 1

            # Append portfolio data to formatted_data_dict
            formatted_data_dict["data"].append(
                {
                    "x": analysis.returns.index.strftime("%Y-%m-%d").tolist(),
                    "y": cumulative_returns.tolist(),
                    "c": portfolio["sharpe_ratio"],
                    "tooltip": portfolio["tooltip"],
                }
            )
        return formatted_data_dict

    def crunch(self, portfolio_data, analysis, comparison):
        # Reorganize the computed properties so it's ready for plotting in the front-end
        formatted_data = []

        for series_name, portfolios in portfolio_data.items():
            print("=" * 100)
            formatted_data.append(
                self.format_portfolio_data(
                    series_name=series_name, portfolios=portfolios, analysis=analysis
                )
            )

        return formatted_data
