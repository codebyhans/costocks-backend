class plotPrices:
    def __init__(self, analysis):
        # Prepare data
        self.data = self.crunch(analysis)

    def crunch(self, analysis):
        # Extract unique pairs of level_1 indices
        # Create traces
        data = []
        for tick in analysis["prices"].columns:
            xs = analysis["prices"].index
            ys = analysis["prices"][tick]
            datapoints = []
            for x, y in zip(xs, ys):
                datapoint = {
                    "x": x,
                    "y": y,
                }
                datapoints.append(datapoint)
            # Create a scatter trace for each pair
            data.append(datapoints)

        formatted_data = []

        # Reorganize the computed properties so it's ready for plotting in the front-end
        # for key, portfolios in data.items():
        #    formatted_data_dict = {}
        #    datapoints = []
        #    for portfolio in portfolios["portfolios"]:
        #        datapoint = {
        #            "x": portfolio["x"],
        #            "y": portfolio["y"],
        #        }
        #        datapoints.append(datapoint)
        #
        #    # determine if data should be connected
        #    formatted_data_dict["seriesName"] = key
        #    formatted_data_dict["data"] = datapoints
        #
        #    formatted_data.append(formatted_data_dict)
        #
        # print(formatted_data)

        return formatted_data
