from components.fetch_data_component import Financial
from components.fetch_data_component import VolatilityMinimizer
from components.fetch_data_component import PreWeighted
from components.fetch_data_component import Sharpe


class plotCummulitativeReturns:
    def __init__(self, analysis):
        # Prepare data
        self.data = self.crunch(analysis)

        # Construct figure layout
        self.layout = self.layout(self.data)

        # Define figure
        self.fig = go.Figure(data=self.data, layout=self.layout)

    def crunch(self, analysis):
        sharpe_portfolio = Financial.create_portfolio(
            df=analysis["df"],
            cov_matrix=analysis["cov"],
            constructor=Sharpe,
            name="Sharpe ratio optimal portfolio",
        )

        for port in sharpe_portfolio.portfolios:
            weighted_returns = analysis.returns.multiply(port.weights.values, axis=1)
            weighted_returns["sharpe_optimal_portfolio"] = weighted_returns.sum(axis=1)
        #

        return {
            "data": data,
            "ymins": [ymins],
            "ymaxs": [ymaxs],
            "xmins": [0],
            "xmaxs": [1.10 * max([max(efficient_frontier.volatilities)])],
        }

    def layout(self, data):
        return go.Layout(
            title="Efficient Frontier",
            xaxis=dict(range=[min(data["xmins"]), max(data["xmaxs"])]),
            yaxis=dict(
                range=[
                    min(data["ymins"]),
                    max(data["ymaxs"]),
                ],
                title="Expected return",
            ),
        )
