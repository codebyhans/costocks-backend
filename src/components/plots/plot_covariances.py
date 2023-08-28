class plotCovariances:
    def __init__(self, analysis):
        # Prepare data
        self.data = self.crunch(analysis)

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
                    data.append({"x": x, "y": y, "desc": f"{pair1} vs {pair2}"})

        return data
