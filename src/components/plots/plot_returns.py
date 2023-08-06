import datetime as dt
from app import app


class plotReturns:
    def __init__(self, analysis):
        # Prepare data
        self.data = self.crunch(analysis)

    def crunch(self, analysis):
        data = {}
        for tick in analysis["returns"].columns:
            values = analysis["returns"][
                tick
            ].tolist()  # Convert pandas Series to a Python list
            data[tick] = {"values": values}

            return data
