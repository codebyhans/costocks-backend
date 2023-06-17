import plotly.graph_objs as go
from components.fetch_data_component import Financial
import numpy as np
import datetime as dt
from app import app


class plotBenchmark:
    def __init__(self, analysis, comparison):
        # Prepare data
        data = self.crunch(analysis, comparison)

        # Define figure
        self.fig = go.Figure(data=data)

        # Generate tick positioning
        tick_positions = [
            dt.date(app.year, 1, 1),
            dt.date(app.year, 4, 1),
            dt.datetime(app.year, 7, 1),
            dt.date(app.year, 10, 1),
            dt.date(app.year, 12, 31),
        ]

        # Find the tick labels
        tick_labels = [d.strftime("%b %d") for d in tick_positions]
        self.fig.update_layout(
            height=600,
            width=1600,
            title="Prices",
            xaxis_range=[dt.date(app.year, 1, 1), dt.date(app.year, 12, 31)],
            xaxis=dict(
                tickmode="array",
                tickvals=tick_positions,
                ticktext=tick_labels,
                title="Date",
            ),
            yaxis=dict(
                range=[
                    min([0, min(data["ymins"])]),
                    max(data["ymaxs"]),
                ],
                title="Accumulated return",
            ),
        )

    def crunch(self, analysis, comparison):
        # Create the analysis portfolio
        analysis_portfolios = Financial.create_portfolio(
            df=analysis["df"],
            cov_matrix=analysis["cov"],
            name="Analysis portfolio",
            plotas="markers",
            symbol="x",
            color="black",
        )
        comparison_portfolios = Financial.create_portfolio(
            df=comparison["df"],
            cov_matrix=comparison["cov"],
            name="Comparison portfolio",
            plotas="markers",
            symbol="x",
            color="red",
        )
        data = []
        ymaxs = []
        ymins = []
        for portfolio, dict in [
            (analysis_portfolios, analysis),
            (comparison_portfolios, comparison),
        ]:
            weights = portfolio.portfolios[0].weights
            returns = dict["returns"]

            weighted_returns = weights.multiply(returns)

            summed_weighted_returns = 1 + weighted_returns.sum(axis=1) / 100

            # ensure everything is compared to first day of period
            summed_weighted_returns.iloc[0] = 1

            # Extract unique pairs of level_1 indices
            # Create traces

            x = summed_weighted_returns.index
            y = (summed_weighted_returns.cumprod() - 1) * 100
            ymins.append(np.nanmin(y.values))
            ymaxs.append(np.nanmax(y.values))

            # Create a scatter trace for each pair
            data.append(go.Scatter(x=x, y=y, name=portfolio.name))

        return {"data": data, "ymins": ymins, "ymaxs": ymaxs}
