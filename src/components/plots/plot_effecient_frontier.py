import plotly.graph_objs as go
import numpy as np
import json
import datetime as dt
from app import app
from components.fetch_data_component import Financial
from components.fetch_data_component import VolatilityMinimizer
from components.fetch_data_component import PreWeighted
from components.fetch_data_component import Sharpe


class ploteffecientFrontier:
    def __init__(self, analysis, comparison):
        # Prepare data
        self.data = self.crunch(analysis, comparison)

    def crunch(self, analysis, comparison):
        sharpe_portfolio = Financial.create_portfolio(
            df=analysis["df"],
            cov_matrix=analysis["cov"],
            constructor=Sharpe,
            mode=None,
            name="Sharpe ratio optimal portfolio",
            backgroundColor="rgba(255, 99, 132, 0.6)",
            borderColor="rgba(255, 99, 132, 1)",
        )

        min_variance_portfolio = Financial.create_portfolio(
            df=analysis["df"],
            cov_matrix=analysis["cov"],
            constructor=VolatilityMinimizer,
            name="Minimal variance portfolio",
            backgroundColor="rgba(75, 192, 192, 0.6)",
            borderColor="rgba(75, 192, 192, 1)",
        )
        efficient_frontier = Financial.create_portfolio(
            df=analysis["df"],
            cov_matrix=analysis["cov"],
            constructor=VolatilityMinimizer,
            name="Effecient frontier",
            constrains=np.linspace(
                min(analysis["df"]["expected_return"]),
                max(analysis["df"]["expected_return"]),
                100,
            ),
            connected=True,
            backgroundColor="rgba(54, 162, 235, 0.6)",
            borderColor="rgba(54, 162, 235, 1)",
        )
        all_in_one_portfolios = Financial.create_portfolio(
            df=analysis["df"],
            cov_matrix=analysis["cov"],
            constructor=PreWeighted,
            name="All-in-one portfolios",
            constrains=Financial.all_in_one_portfolios(len(analysis["df"])),
            backgroundColor="rgba(255, 205, 86, 0.6)",
            borderColor="rgba(255, 205, 86, 1)",
        )
        random_portfolios = Financial.create_portfolio(
            df=analysis["df"],
            cov_matrix=analysis["cov"],
            constructor=PreWeighted,
            name="Random portfolios",
            constrains=Financial.random_portfolios(100, len(analysis["df"])),
            backgroundColor="rgba(201, 203, 207, 0.6)",
            borderColor="rgba(204, 203, 207, 1)",
        )
        analysis_portfolios = Financial.create_portfolio(
            df=analysis["df"],
            cov_matrix=analysis["cov"],
            name="Analysis portfolio",
            backgroundColor="rgba(153, 102, 255, 0.6)",
            borderColor="rgba(153, 102, 255, 1)",
        )

        if comparison is not None:
            comparison_portfolios = Financial.create_portfolio(
                df=comparison["df"],
                cov_matrix=comparison["cov"],
                name="Benchmark portfolio",
            )
            comparison_returns = comparison_portfolios.expected_returns
        else:
            comparison_returns = [0]

        # Generate the second scatter graph
        data = {
            "Your portfolio": analysis_portfolios,
            "Portfolio of maximum sharpe-ratio": sharpe_portfolio,
            "Portfolio of minimum variance": min_variance_portfolio,
            "All invested in one stock": all_in_one_portfolios,
            "The effecient frontier": efficient_frontier,
            "Random portfolios": random_portfolios,
        }
        if comparison is not None:
            data["comparison"] = comparison_portfolios

        formatted_data = []

        # Reorganize the computed properties so it's ready for plotting in the front-end
        for key, portfolios in data.items():
            formatted_data_dict = {}
            datapoints = []
            for portfolio in portfolios["portfolios"]:
                datapoint = {
                    "x": portfolio["volatility"],
                    "y": portfolio["expected_return"],
                    "c": portfolio["sharpe_ratio"],
                    "tooltip": portfolio["tooltip"],
                }
                datapoints.append(datapoint)

            # determine if data should be connected
            formatted_data_dict["seriesName"] = key
            formatted_data_dict["connected"] = portfolios["connected"]
            formatted_data_dict["backgroundColor"] = portfolios["backgroundColor"]
            formatted_data_dict["borderColor"] = portfolios["borderColor"]
            formatted_data_dict["data"] = datapoints

            formatted_data.append(formatted_data_dict)

        return formatted_data
