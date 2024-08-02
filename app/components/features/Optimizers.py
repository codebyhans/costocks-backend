import numpy as np
import pandas as pd
from cvxopt import matrix, solvers
import numpy as np
import pandas as pd
from core.financial import Financial
from cvxopt import matrix, solvers

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
                return (result.success, np.round(result.x, decimals=4))
            else:
                return (False, None)

    class Sharpe:
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

        def optimize(self):
            uhat = self.returns - self.rf

            # Check if at least one component of self.returns is larger than self.rf
            if not any(uhat > 0):
                # If none satisfy the condition, set all weights to 0
                zero_weights = [0] * len(self.returns)
                return (True, zero_weights)

            n = len(self.cov_matrix)
            p = self.cov_matrix.values
            P = matrix(0.5 * (p + p.transpose()))  # this is a positive definite matrix
            q = matrix(np.zeros(n))
            G = matrix(np.diag(-np.ones(n)))
            h = matrix(np.zeros(n))
            A = matrix(np.array(uhat), (1, n))
            b = matrix(np.array([1.0]))

            # problem = Problem(P, q, G, h, A, b, lb, ub)
            # solution = solve_problem(problem, solver="cvxopt")
            # Remapping to fractions due to qp formulation

            sol = solvers.qp(P=P, q=q, G=G, h=h, A=A, b=b)
            X = sol["x"] / np.sum(sol["x"])
            return (
                True if sol["status"] == "optimal" else False,
                np.round(X, decimals=4),
            )

        # def optimize(self):
        #    n = len(self.returns)
        #    bounds = [(0, 1) for i in range(n)]
        #    constraints = {"type": "eq", "fun": lambda x: np.sum(x) - 1}
        #    initial_guess = np.array([1 / n for i in range(n)])
        #    result = minimize(
        #        lambda x: -Financial().sharpe_ratio(
        #            self.returns, x, self.cov_matrix, rf=self.rf
        #        ),
        #        initial_guess,
        #        method="SLSQP",
        #        bounds=bounds,
        #        constraints=constraints,
        #        tol=1e-6,  # Set your desired tolerance here
        #    )
        #    # weights = pd.DataFrame(
        #    #    data=result.x, index=self.cov_matrix.index, columns=["weights"]
        #    # )
        #    return (result.success, result.x)

    class PreWeighted:
        """
        PreWeighted portfolio optimization class.

        This class represents a portfolio optimization technique that
        pre-assigns weights based on an equilibrium return.
        It can be used to generate portfolio weights without further optimization.

        Parameters:
        returns (array-like): An array or list of asset returns.
        cov_matrix (array-like): The covariance matrix of the assets.
        constrain (float): The equilibrium return used to pre-assign weights.
        counter (int): An optional counter or identifier for the instance.
        mode (str): An optional mode or configuration identifier.

        Attributes:
        returns (array-like): An array or list of asset returns.
        equilibrium_return (float): The equilibrium return for pre-assigning weights.
        cov_matrix (array-like): The covariance matrix of the assets.
        counter (int): An optional counter or identifier.
        weights (float): The pre-assigned portfolio weights.

        Example:
        >>> returns = [0.1, 0.15, 0.12]
        >>> cov_matrix = [[0.04, 0.02, 0.01],
        ...               [0.02, 0.03, 0.015],
        ...               [0.01, 0.015, 0.02]]
        >>> constrain = 0.1
        >>> pre_weighted = PreWeighted(returns, cov_matrix, constrain)
        >>> pre_weighted.weights
        ?
        """

        def __init__(
            self, returns=None, cov_matrix=None, constrain=None, counter=None, mode=None
        ):
            self.returns = returns
            self.equilibrium_return = constrain
            self.cov_matrix = cov_matrix
            self.counter = counter
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

        def optimize(self):
            return (True, self.equilibrium_return)

    class VolatilityMinimizer:
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
            self, returns=None, cov_matrix=None, constrain=None, counter=None, mode=None
        ):
            self.returns = returns
            self.equilibrium_return = constrain
            self.cov_matrix = cov_matrix
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

        def optimize(self):
            n = len(self.cov_matrix)
            p = self.cov_matrix.values
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

    class MaxReturn:
        """
        <desc missing>
        """

        def __init__(
            self, returns=None, cov_matrix=None, constrain=None, counter=None, mode=None
        ):
            self.returns = returns
            self.equilibrium_return = constrain
            self.cov_matrix = cov_matrix
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

        def optimize(self):
            # Find the index of the maximum value in the input array
            max_index = np.argmax(self.returns)

            # Create an array of zeros with the same length as the input array
            x = np.zeros_like(self.returns)

            # Set the value at the max_index to 1
            x[max_index] = 1

            return (True, x)