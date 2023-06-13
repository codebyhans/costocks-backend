import plotly.graph_objs as go
import numpy as np
import datetime as dt
from app import app
from components.fetch_data_component import Financial
from components.fetch_data_component import VolatilityMinimizer
from components.fetch_data_component import PreWeighted
from components.fetch_data_component import Sharpe


class ploteffecientFrontier:
    def __init__(self, analysis,comparison):
        # Prepare data
        data = self.crunch(analysis,comparison)

        # Define figure
        self.fig = go.Figure(data=data)
        self.fig.update_layout(
            height=600,
            width=1600,
            title="Efficient Frontier",
            xaxis=dict(range=[min(data["xmins"]), max(data["xmaxs"])], title="Standard deviation, %"),
            yaxis=dict(
                range=[
                    min(data["ymins"]),
                    max(data["ymaxs"]),
                ],
                title="Mean return, %",
            ),
        )



    def crunch(self, analysis,comparison):
        sharpe_portfolio = Financial.create_portfolio(
            df=analysis["df"],
            cov_matrix=analysis["cov"],
            constructor=Sharpe,
            mode=None,
            name="Sharpe ratio optimal portfolio",
            symbol="cross",
            color="red",
            size=10,
        )

        #sharpe_portfolio_int = Financial.create_portfolio(
        #    df=analysis["df"],
        #    cov_matrix=analysis["cov"],
        #    constructor=Sharpe,
        #    mode = 'int',
        #    name="Sharpe ratio optimal portfolio (int)",
        #    symbol="cross",
        #    color="blue",
        #    size=8,
        #)

        min_variance_portfolio = Financial.create_portfolio(
            df=analysis["df"],
            cov_matrix=analysis["cov"],
            constructor=VolatilityMinimizer,
            name="Minimal variance portfolio",
            color="orange",
            size=10,
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
            plotas="lines",
        )
        all_in_one_portfolios = Financial.create_portfolio(
            df=analysis["df"],
            cov_matrix=analysis["cov"],
            constructor=PreWeighted,
            name="All-in-one portfolios",
            constrains=Financial.all_in_one_portfolios(len(analysis["df"])),
            plotas="markers",
            color="red",
            size=10,
        )
        capacity = 10000
        prices = analysis['prices'].tail(1).values.tolist()[0]
        random_portfolios = Financial.create_portfolio(
            df=analysis["df"],
            cov_matrix=analysis["cov"],
            constructor=PreWeighted,
            name="Random portfolios",
            constrains=Financial.random_portfolios(capacity, prices),
            plotas="markers",
        )
        print(random_portfolios.portfolios[0])
        analysis_portfolios = Financial.create_portfolio(
            df=analysis["df"],
            cov_matrix=analysis["cov"],
            name="Analysis portfolio",
            plotas="markers",
            symbol="x",
            color="black",
        )

        if comparison is not None:
            comparison_portfolios = Financial.create_portfolio(
                df=comparison["df"],
                cov_matrix=comparison["cov"],
                name="Benchmark portfolio",
                plotas="markers",
                symbol="circle-dot",
                color="black",
            )
            comparison_returns = comparison_portfolios.expected_returns
        else:
            comparison_returns = [0]


        # Generate the second scatter graph
        if comparison is not None:
            data = [
                efficient_frontier.plot,
                random_portfolios.plot,
                all_in_one_portfolios.plot,
                min_variance_portfolio.plot,
                sharpe_portfolio.plot,
                analysis_portfolios.plot,
                comparison_portfolios.plot,
            ]
        else: 
            data = [
                efficient_frontier.plot,
                random_portfolios.plot,
                all_in_one_portfolios.plot,
                min_variance_portfolio.plot,
                sharpe_portfolio.plot,
                analysis_portfolios.plot,
            ]
        min_return = min(efficient_frontier.expected_returns+comparison_returns+[0])
        max_return = max(efficient_frontier.expected_returns+comparison_returns)
        
        diff = 0.25 * max_return - min_return
        ymins = min_return - diff
        ymaxs = max_return + diff

        return {
            "data": data,
            "ymins": [ymins],
            "ymaxs": [ymaxs],
            "xmins": [0],
            "xmaxs": [1.10 * max([max(efficient_frontier.volatilities)])],
        }
