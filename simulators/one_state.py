"""Simulator of the one-state motor-adaptation model.

Model, symbols and sign convention: decision 0005 and docs/models/one_state.md.
Parameter order everywhere: theta = (A, B, sigma_eta, sigma_epsilon).
"""

import numpy as np


def simulate_sitting(rng, theta, p, v, size=()):
    """Simulate the movement angles of one or more sittings.

    Runs the model of decision 0005 forward, one trial at a time::

        x[0] ~ N(0, sigma_eta^2)
        y[t] = x[t] + epsilon[t],                 epsilon[t] ~ N(0, sigma_epsilon^2)
        e[t] = y[t] + p[t]
        x[t+1] = A x[t] - B v[t] e[t] + eta[t],   eta[t] ~ N(0, sigma_eta^2)

    Several sittings that share the parameters and the schedule are simulated at once
    (vectorized over `size`); the loop over trials is the model's recursion.

    Parameters
    ----------
    rng : numpy.random.Generator
        Source of all the noise. It is advanced by the draws (the only side effect).
    theta : array_like of float, shape (4,)
        Parameters (A, B, sigma_eta, sigma_epsilon): retention and adaptation rate,
        each strictly between 0 and 1, and the standard deviations of the planning
        and execution noise, each positive. In units of the perturbation size.
    p : array_like of float, shape (T,)
        Perturbation on each trial, added to the movement to give the error.
    v : array_like of {0, 1}, shape (T,)
        Vision flag on each trial: 1 if the cursor is shown, so the subject learns from
        the error; 0 if not, so the plan only decays and picks up planning noise.
    size : tuple of int, optional
        Number of independent sittings to simulate, as an array shape. Default ``()``:
        one sitting.

    Returns
    -------
    y : numpy.ndarray of float, shape (*size, T)
        Movement angle on every trial of every sitting.

    Raises
    ------
    ValueError
        If theta does not have shape (4,), a parameter is outside its domain, p or v is
        not one-dimensional, p and v differ in length, or v holds values other than
        0 and 1.
    """
    theta = np.asarray(theta, dtype=float)
    p = np.asarray(p, dtype=float)
    v = np.asarray(v)
    if theta.shape != (4,):
        raise ValueError(f"theta must have shape (4,), got {theta.shape}")
    A, B, sigma_eta, sigma_epsilon = theta
    if not (0 < A < 1 and 0 < B < 1):
        raise ValueError(f"A and B must be strictly between 0 and 1, got A={A}, B={B}")
    if not (sigma_eta > 0 and sigma_epsilon > 0):
        raise ValueError(
            "sigma_eta and sigma_epsilon must be positive, got "
            f"sigma_eta={sigma_eta}, sigma_epsilon={sigma_epsilon}"
        )
    if p.ndim != 1 or v.ndim != 1:
        raise ValueError(
            f"p and v must be one-dimensional, got shapes {p.shape} and {v.shape}"
        )
    if len(p) != len(v):
        raise ValueError(
            f"p and v must have the same length, got {len(p)} and {len(v)}"
        )
    if not np.all((v == 0) | (v == 1)):
        raise ValueError("v must contain only 0 and 1")

    y = np.empty((*size, len(p)))
    x = rng.normal(0.0, sigma_eta, size)  # the first plan
    for t in range(len(p)):
        y[..., t] = x + rng.normal(0.0, sigma_epsilon, size)
        e = y[..., t] + p[t]
        x = A * x - B * v[t] * e + rng.normal(0.0, sigma_eta, size)
    return y
