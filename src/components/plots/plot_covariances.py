import plotly.graph_objs as go
import numpy as np
import datetime as dt
from app import app


class plotCovariances:
    def __init__(self, analysis):
        # Prepare data
        data = self.crunch(analysis)

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
            title="Covariances",
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
                title="Covariance coefficient",
            ),
        )

    def crunch(self, analysis):
        # Extract unique pairs of level_1 indices
        pairs = analysis["rolling_cov"].index.levels[1].unique().tolist()
        n_pairs = len(pairs)
        # Create traces
        data = []
        ymaxs = []
        ymins = []
        for i in range(n_pairs):
            for j in range(i, n_pairs):
                pair1 = pairs[i]
                pair2 = pairs[j]
                if pair1 != pair2:
                    # Filter the data to the specified pair
                    d = analysis["rolling_cov"].loc[(slice(None), [pair1]), (pair2)]
                    d = d.reset_index()
                    x = d["Date"]
                    y = d[pair2]
                    ymins.append(np.nanmin(y.values))
                    ymaxs.append(np.nanmax(y.values))

                    # Create a scatter trace for each pair
                    data.append(go.Scatter(x=x, y=y, name=f"{pair1} vs {pair2}"))

        return {"data": data, "ymins": ymins, "ymaxs": ymaxs}
