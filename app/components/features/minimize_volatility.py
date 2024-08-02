import numpy as np
import pandas as pd
from cvxopt import matrix, solvers
import numpy as np
import pandas as pd

solvers.options["show_progress"] = False
solvers.options['abstol'] = 10**-12
solvers.options['reltol'] = 10**-12

class MinimizerVolatility:
    """
    Portfolio optimization class for minimizing portfolio volatility.

    This class represents a portfolio optimization technique that
    aims to minimize portfolio volatility, subject to constraints.
    It utilizes the SciPy library's minimize function with SLSQP
    (Sequential Least Squares Quadratic Programming) method to find
    the optimal asset weights that minimize portfolio volatility.

    Parameters:
    returns (array-like): An array or list of asset returns.
    cov_matrix (array-like): The covariance matrix of the assets.
    constrain (float): The equilibrium return used as a constraint for the portfolio.
    counter (int): An optional counter or identifier for the instance.
    mode (str): An optional mode or configuration identifier.

    Attributes:
    returns (array-like): An array or list of asset returns.
    equilibrium_return (float): The equilibrium return used as a constraint.
    cov_matrix (array-like): The covariance matrix of the assets.
    weights (DataFrame): The optimal portfolio weights that minimize portfolio volatility.

    Example:
    >>> returns = [0.1, 0.15, 0.12]
    >>> cov_matrix = [[0.04, 0.02, 0.01],
    ...               [0.02, 0.03, 0.015],
    ...               [0.01, 0.015, 0.02]]
    >>> constrain = 0.1
    >>> vol_minimizer = VolatilityMinimizer(returns, cov_matrix, constrain)
    >>> vol_minimizer.weights
       weights
    0      ?
    1      ?
    2      ?

    """

    def __init__(
        self, returns=None, cov_matrix=None, constrain=None
    ):
        self.returns = returns
        self.equilibrium_return = constrain
        self.cov_matrix = cov_matrix
        

    def optimize(self):
        n = len(self.cov_matrix)
        p = self.cov_matrix
        P = matrix(0.5 * (p + p.transpose()))  # this is a positive definite matrix
        q = matrix(np.zeros(n))
        G = matrix(np.diag(-np.ones(n)))
        h = matrix(np.zeros(n))
        if self.equilibrium_return is not None:
            A = matrix(np.array([[1.0] * n, self.returns]))
            b = matrix(np.array([1.0, self.equilibrium_return]))
        else:
            A = matrix(np.array([1.0] * n), (1, n))
            b = matrix(np.array([1.0]))

        sol = solvers.qp(P=P, q=q, G=G, h=h, A=A, b=b)
        return (
            True if sol["status"] == "optimal" else False,
            np.round(sol["x"], decimals=4),
        )
