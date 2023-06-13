import plotly.graph_objs as go
import numpy as np
import datetime as dt
from app import app


class plotPrices:
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
                title="Price",
            ),
        )

    def crunch(self, analysis):
        # Extract unique pairs of level_1 indices
        pairs = analysis["prices"]
        # Create traces
        data = []
        ymaxs = []
        ymins = []
        for tick in analysis["prices"].columns:
            x = analysis["prices"].index
            y = analysis["prices"][tick]
            ymins.append(np.nanmin(y.values))
            ymaxs.append(np.nanmax(y.values))

            # Create a scatter trace for each pair
            data.append(go.Scatter(x=x, y=y, name=f"{tick}"))

        return {"data": data, "ymins": ymins, "ymaxs": ymaxs}
