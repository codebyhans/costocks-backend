from cvxopt import matrix, solvers
from core.financial import Financial
import numpy as np 
import pandas as pd
solvers.options["show_progress"] = False
solvers.options['abstol'] = 10**-12
solvers.options['reltol'] = 10**-12

class Optimizers:
    class HolyGrail:
        """
        Portfolio optimization class for maximizing the Sharpe Ratio/stocks.
        """

        def __init__(
            self,
            returns,
            cov_matrix=None,
            rf=0.0,
            constrain=None,
            counter=None,
            mode=None,
        ):
            self.returns = returns
            self.cov_matrix = cov_matrix
            self.rf = rf
            self.mode = mode
            success, weights = self.optimize()
            if success:
                self.weights = pd.DataFrame(
                    data=weights, index=self.cov_matrix.index, columns=["weights"]
                )
            else:
                zero_weights = [0] * len(self.cov_matrix.index)
                self.weights = pd.DataFrame(
                    data=zero_weights, index=self.cov_matrix.index, columns=["weights"]
                )

        def heaviside(self, x, beta=4, eta=0.5):
            n = np.tanh(beta * eta) + np.tanh(beta * (x - eta))
            d = np.tanh(beta * eta) + np.tanh(beta * (1 - eta))
            return n / d

        def count_non_zeros(self, arr):
            return np.count_nonzero(arr)

        def smooth_count(self, x, beta=4, eta=0.5):
            ones = np.ones_like(x)
            h = self.heaviside(x, beta=beta, eta=eta)
            count = np.dot(ones, h)

            return count

        def optimize(self):
            n = len(self.returns)
            bounds = [(0, 1) for i in range(n)]
            constraints = {"type": "eq", "fun": lambda x: np.sum(x) - 1}
            beta0 = 1
            eta = 0.0001
            # Use the solution from s sharpe optimizatio for intial guess here
            sharpe = Optimizers.Sharpe(self.returns, self.cov_matrix, self.rf)

            if any(sharpe.weights > 0):
                beta = beta0
                initial_guess = sharpe.weights.values.flatten()

                devisor = self.smooth_count(initial_guess, beta=beta, eta=eta)
                count = self.count_non_zeros(np.round(initial_guess, decimals=9))
                first_run = True
                while abs(count - devisor) > 0.01 or first_run:
                    first_run = False
                    result = minimize(
                        lambda x: -Financial().sharpe_ratio(
                            self.returns, x, self.cov_matrix, rf=self.rf
                        )
                        / self.smooth_count(x, beta=beta, eta=eta),
                        initial_guess,
                        method="SLSQP",
                        bounds=bounds,
                        constraints=constraints,
                        tol=1e-6,  # Set your desired tolerance here
                    )
                    if result.success:
                        beta = beta + 0.2
                        devisor = self.smooth_count(result.x, beta=beta, eta=eta)
                        count = self.count_non_zeros(np.round(result.x, decimals=4))
                        initial_guess = result.x
                    else:
                        return False, None
                return (result.success, result.x)
            else:
                return (False, None)