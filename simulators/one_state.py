"""Simulator of the one-state motor-adaptation model, with its prior and schedules.

Model, symbols, sign convention, priors and schedules: decision 0005 and
docs/models/one_state.md. Parameter order everywhere:
theta = (A, B, sigma_eta, sigma_epsilon).
"""

import numpy as np
from scipy.special import expit

# The four kinds of block, in this order: perturbation p and vision flag v of each.
BLOCK_KINDS = ("baseline", "+1", "-1", "no vision")
BLOCK_P = np.array([0.0, 1.0, -1.0, 0.0])
BLOCK_V = np.array([1, 1, 1, 0])


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


def sample_prior(
    rng,
    size,
    *,
    mu_logit_A,
    sigma_logit_A,
    mu_logit_B,
    sigma_logit_B,
    mu_log_sigma_epsilon,
    sigma_log_sigma_epsilon,
    mu_log_ratio,
    sigma_log_ratio,
):
    """Draw parameter vectors from the prior of decision 0005.

    Each prior is normal on an unbounded scale and is then transformed::

        A             = expit(N(mu_logit_A, sigma_logit_A))
        B             = expit(N(mu_logit_B, sigma_logit_B))
        sigma_epsilon = exp(N(mu_log_sigma_epsilon, sigma_log_sigma_epsilon))
        sigma_eta     = sigma_epsilon * exp(N(mu_log_ratio, sigma_log_ratio))

    so the planning noise is given a prior through its ratio to the execution noise.
    The four normal draws are independent.

    Parameters
    ----------
    rng : numpy.random.Generator
        Source of the draws. It is advanced (the only side effect).
    size : int
        Number of parameter vectors to draw.
    mu_logit_A, sigma_logit_A : float
        Mean and standard deviation of logit(A).
    mu_logit_B, sigma_logit_B : float
        Mean and standard deviation of logit(B).
    mu_log_sigma_epsilon, sigma_log_sigma_epsilon : float
        Mean and standard deviation of log(sigma_epsilon).
    mu_log_ratio, sigma_log_ratio : float
        Mean and standard deviation of log(sigma_eta / sigma_epsilon).

    Returns
    -------
    theta : numpy.ndarray of float, shape (size, 4)
        Columns (A, B, sigma_eta, sigma_epsilon), in the order `simulate_sitting`
        takes them.
    """
    A = expit(rng.normal(mu_logit_A, sigma_logit_A, size))
    B = expit(rng.normal(mu_logit_B, sigma_logit_B, size))
    log_sigma_epsilon = rng.normal(mu_log_sigma_epsilon, sigma_log_sigma_epsilon, size)
    log_ratio = rng.normal(mu_log_ratio, sigma_log_ratio, size)
    sigma_epsilon = np.exp(log_sigma_epsilon)
    sigma_eta = np.exp(log_sigma_epsilon + log_ratio)
    return np.column_stack([A, B, sigma_eta, sigma_epsilon])


def sample_schedule(
    rng,
    *,
    n_blocks_min,
    n_blocks_max,
    mu_log_block_len,
    sigma_log_block_len,
    kind_concentration,
):
    """Draw the schedule of one sitting: perturbation and vision on every trial.

    Following decision 0005: the number of blocks is uniform on
    n_blocks_min..n_blocks_max; block lengths are independent and log-normal, rounded
    to whole trials; the sitting's proportions of the four kinds of block
    (`BLOCK_KINDS`) are drawn from a symmetric Dirichlet with the given concentration;
    the first block is a baseline and every later block's kind is drawn independently
    with those proportions. Two neighbouring blocks of the same kind are, in effect, one
    longer block.

    Parameters
    ----------
    rng : numpy.random.Generator
        Source of the draws. It is advanced (the only side effect).
    n_blocks_min, n_blocks_max : int
        Smallest and largest number of blocks, both included; 1 <= min <= max.
    mu_log_block_len, sigma_log_block_len : float
        Mean and standard deviation of the log of a block's length in trials.
    kind_concentration : float
        Concentration of the symmetric Dirichlet over the four kinds, for each kind.
        Larger values make the four proportions more alike.

    Returns
    -------
    p : numpy.ndarray of float, shape (T,)
        Perturbation on each trial: 0, +1 or -1 (0 on no-vision trials).
    v : numpy.ndarray of int, shape (T,)
        Vision flag on each trial: 1, or 0 in no-vision blocks.

    Raises
    ------
    ValueError
        If the block counts do not satisfy 1 <= n_blocks_min <= n_blocks_max.
    """
    if not 1 <= n_blocks_min <= n_blocks_max:
        raise ValueError(
            "need 1 <= n_blocks_min <= n_blocks_max, got "
            f"n_blocks_min={n_blocks_min}, n_blocks_max={n_blocks_max}"
        )
    n_blocks = rng.integers(n_blocks_min, n_blocks_max + 1)
    log_len = rng.normal(mu_log_block_len, sigma_log_block_len, n_blocks)
    block_len = np.rint(np.exp(log_len)).astype(int)
    proportions = rng.dirichlet(np.full(len(BLOCK_KINDS), kind_concentration))
    later_kinds = rng.choice(len(BLOCK_KINDS), size=n_blocks - 1, p=proportions)
    kind = np.concatenate([[0], later_kinds])  # the first block is a baseline
    return np.repeat(BLOCK_P[kind], block_len), np.repeat(BLOCK_V[kind], block_len)
