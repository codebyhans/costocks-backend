import unittest
import pandas as pd
import numpy as np
from maximize_sharpe import MaximizeSharpe
from minimize_volatility import MinimizerVolatility
from data.models import TimeSeries, TimeSeriesCollection

class TestMinimizerVolatility(unittest.TestCase):
    """
    Class containing all the tests for the submodule Optimizers
    """

    cov_matrix = np.array(
        [[0.02, 0.0036, 0.0022], [0.0036, 0.0218, 0.0052], [0.0022, 0.0052, 0.0398]],
    )
    returns = np.array([1.0, 1.5, 3.0])
    rf = 1.17


    timeseries=[]
    for ticker in tickers.keys():
        timeseries_data = {ticker: tickers[ticker]}
        timeseries.append(TimeSeries(series=timeseries_data)
        )
    timeseriescollection = TimeSeriesCollection(collection=timeseries)

    def test_sharpe_optimizer(self):
        # Test the Sharpe optimizer
        epsilon = 0.001
        expected_sharpe_ratio = 9.1942631342836

        # Find weights at the Sharpe point
        status, weigts = MaximizeSharpe(
            returns=self.returns, cov_matrix=self.cov_matrix, rf=self.rf
        )

        # Find properties at optimized solution
        volatility_minimizer_optimizer = Financial().portfolio_return(
            returns=self.asset_returns,
            weights=sharpe_optimizer.weights["weights"].tolist(),
        )

        # Find two points in the vicinity of the the sharpe point
        volatility_minimizer_optimizer_plus = MinimizerVolatility(
            returns=self.returns,
            cov_matrix=self.cov_matrix,
            constrain=optimized_return + epsilon,
        )

        volatility_minimizer_optimizer_minus = MinimizerVolatility(
            returns=self.returns,
            cov_matrix=self.cov_matrix,
            constrain=optimized_return - epsilon,
        )




        sharpes = [
            Financial().sharpe_ratio(
                returns=self.returns,
                weights=sharpe_optimizer.weights["weights"],
                cov_matrix=self.cov_matrix,
                rf=self.rf,
            ),
            Financial().sharpe_ratio(
                returns=self.returns,
                weights=volatility_minimizer_optimizer_plus.weights["weights"],
                cov_matrix=self.cov_matrix,
                rf=self.rf,
            ),
            Financial().sharpe_ratio(
                returns=self.returns,
                weights=volatility_minimizer_optimizer_minus.weights["weights"],
                cov_matrix=self.cov_matrix,
                rf=self.rf,
            ),
        ]
        self.assertTrue(
            sharpes[0] == max(sharpes),
            "The identified portfolio is not the one with largest sharpe ratio",
        )
        self.assertAlmostEqual(
            sharpes[0], expected_sharpe_ratio, 6, "Correct sharpe ratio"
        )


if __name__ == "__main__":
    unittest.main()
