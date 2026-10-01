"""Exact likelihood of the one-state motor-adaptation model.

Math: docs/models/one_state.md. Parameter order: theta = (A, B, sigma_x, sigma_y).

`kalman_logp` is the likelihood to use. `joint_gaussian` is a slow, independent
calculation of the same thing, kept as the reference the filter is checked against.
"""

import numpy as np
import pytensor
import pytensor.tensor as pt


def kalman_step(p_t, y_t, m, P, A, B, var_x, var_y):
    """One trial of the filter: score y_t, update on it, predict the next state.

    m and P are the mean and variance of x_t given the earlier responses.
    Returns (m, P) for x_{t+1} and the log density of y_t.
    """
    S = P + var_y  # predictive variance of y_t
    logp_t = -0.5 * (pt.log(2 * np.pi * S) + (y_t - m) ** 2 / S)
    K = P / S
    m_filt = m + K * (y_t - m)
    P_filt = (1 - K) * P
    return A * m_filt + B * (p_t - y_t), A**2 * P_filt + var_x, logp_t


def kalman_logp(y, A, B, sigma_x, sigma_y, p):
    """Symbolic log-likelihood of one sitting, log p(y | theta, p).

    All arguments are PyTensor variables: y and p vectors of the same length, the rest
    scalars. The argument order (value first, then parameters) is the one PyMC expects
    of a log-density, so this can be passed as `logp` to `pm.CustomDist`.
    """
    _, _, logp_t = pytensor.scan(
        kalman_step,
        sequences=[p, y],
        # m_1, P_1, and nothing carried forward for the log density
        outputs_info=[pt.zeros((), dtype="float64"), sigma_x**2, None],
        non_sequences=[A, B, sigma_x**2, sigma_y**2],
        return_updates=False,
    )
    return logp_t.sum()


def joint_gaussian(theta, p):
    """Mean and covariance of a whole sitting's responses, without filtering.

    Runs the model equations on coefficients instead of numbers: each quantity is a row
    of 2T + 1 weights, on eta_1..eta_T, on eps_1..eps_T, and a constant.
    Returns (mean, cov) with shapes (T,) and (T, T).
    """
    A, B, sigma_x, sigma_y = theta
    T = len(p)
    unit = np.eye(2 * T + 1)
    Y = np.empty((T, 2 * T + 1))
    x = unit[0]  # x_1 = eta_1
    for t in range(T - 1):
        Y[t] = x + unit[T + t]
        x = A * x + B * (p[t] * unit[-1] - Y[t]) + unit[t + 1]
    Y[T - 1] = x + unit[2 * T - 1]
    G = Y[:, :-1]  # weights of the responses on the noise terms
    D = np.repeat([sigma_x**2, sigma_y**2], T)  # the noise variances
    return Y[:, -1], (G * D) @ G.T
