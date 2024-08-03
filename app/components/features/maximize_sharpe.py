import numpy as np
import pandas as pd
from cvxopt import matrix, solvers
import numpy as np
import pandas as pd
from cvxopt import matrix, solvers

solvers.options["show_progress"] = False
solvers.options['abstol'] = 10**-12
solvers.options['reltol'] = 10**-12

class MaximizeSharpe:
    """
    Portfolio optimization class for maximizing the Sharpe Ratio.
    This class represents a portfolio optimization technique that
    aims to maximize the Sharpe Ratio, a measure of risk-adjusted return.
    It uses the SciPy library's minimize function with the SLSQP
    (Sequential Least Squares Quadratic Programming) method to find
    the optimal asset weights that maximize the Sharpe Ratio.
    Parameters:
    returns (array-like): An array or list of asset returns.
    cov_matrix (array-like): The covariance matrix of the assets.
    rf (float, optional): The risk-free rate, defaulting to 0.0.
    constrain (float): The equilibrium return used as a constraint for the portfolio.
    counter (int): An optional counter or identifier for the instance.
    mode (str): An optional mode or configuration identifier.
    Attributes:
    returns (array-like): An array or list of asset returns.
    cov_matrix (array-like): The covariance matrix of the assets.
    rf (float): The risk-free rate.
    mode (str): A configuration identifier.
    weights (DataFrame): The optimal portfolio weights that maximize the Sharpe Ratio.
    Example:
    >>> returns = [0.1, 0.15, 0.12]
    >>> cov_matrix = [[0.04, 0.02, 0.01],
    ...               [0.02, 0.03, 0.015],
    ...               [0.01, 0.015, 0.02]]
    >>> rf = 0.03
    >>> constrain = 0.1
    >>> sharpe_optimizer = Sharpe(returns, cov_matrix, rf, constrain)
    >>> sharpe_optimizer.weights
       weights
    0      0.194595
    1      0.630331
    2      0.175074
    https://people.stat.sc.edu/sshen/events/backtesting/reference/maximizing%20the%20sharpe%20ratio.pdf
    """
    def __init__(
        self,
        returns=None,
        cov_matrix=None,
    ):
        self.returns = returns
        self.cov_matrix = cov_matrix
    
    def optimize(self, risk_free_rate: float=0.0):
        uhat = [ret - risk_free_rate for ret in self.returns]
        # Check if at least one component of self.returns is larger than self.rf
        if not any(ret > 0 for ret in uhat):
            # If none satisfy the condition, set all weights to 0
            zero_weights = [0] * len(self.returns)
            return (True, zero_weights)
        n = len(self.cov_matrix)
        p = self.cov_matrix
        P = matrix(0.5 * (p + p.transpose()))  # this is a positive definite matrix
        q = matrix(np.zeros(n))
        G = matrix(np.diag(-np.ones(n)))
        h = matrix(np.zeros(n))
        A = matrix(np.array(uhat), (1, n))
        b = matrix(np.array([1.0]))
        
        #Solve optimization 
        sol = solvers.qp(P=P, q=q, G=G, h=h, A=A, b=b)
        X = sol["x"] / np.sum(sol["x"])
        return (
            True if sol["status"] == "optimal" else False,
            np.round(X, decimals=4),
        )