import unittest
import pandas as pd
import numpy as np
from minimize_volatility import MinimizerVolatility

class TestMinimizerVolatility(unittest.TestCase):
    """
    Class containing all the tests for the submodule Optimizers
    """

    cov_matrix = np.array(
        [[0.02, 0.0036, 0.0022], [0.0036, 0.0218, 0.0052], [0.0022, 0.0052, 0.0398]],
    )
    returns = np.array([1.0, 1.5, 3.0])

    def test_volatility_minimizer_optimizer_unconstrained(self):
        """
        Testing the capability to solving the minimal variance all-weights-positive (otherwise) unconstrained
        problem (section 13.4.2: https://bookdown.org/compfinezbook/introcompfinr/Quadradic-programming.html)

                                    | 0.0200  0.0036  0.0022 |
        For the covariance matrix = | 0.0036  0.0218  0.0052 |
                                    | 0.0022  0.0052  0.0398 |

        The chapter in the link above (26-10-2023) the solution to the problem is x = [0.441, 0.366, 0.193].
        on 26-10-2023, this implementation achieves xhat = [0.440135, 0.365904, 0.193962] which we use for benchmarking
        """

        status, weights = MinimizerVolatility(
            returns=self.returns,
            cov_matrix=self.cov_matrix
        ).optimize()

        # Check if the optimizer returns a valid DataFrame of weights
        #self.assertIsInstance(volatility_minimizer_optimizer.weights, pd.DataFrame)

        # Assert the obtained weights
        self.assertAlmostEqual(
            weights[0], 0.4411, 3
        )
        self.assertAlmostEqual(
            weights[1], 0.3656, 3
        )
        self.assertAlmostEqual(
            weights[2], 0.1932, 3
        )

if __name__ == "__main__":
    unittest.main()
