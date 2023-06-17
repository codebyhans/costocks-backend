import plotly.graph_objs as go
import numpy as np
import datetime as dt
from app import app


class plotReturns:
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
            title="Daily return distribution",
            yaxis=dict(
                title="Frequency (count)",
            ),
            xaxis=dict(title="Daily return, %"),
        )

    def crunch(self, analysis):
        # Extract unique pairs of level_1 indices
        data = []
        ymaxs = None
        ymins = None
        for tick in analysis["returns"].columns:
            x = analysis["returns"][tick]

            # Create a scatter trace for each pair
            data.append(go.Histogram(x=x, name=f"{tick}"))

        return {"data": data, "ymins": ymins, "ymaxs": ymaxs}
