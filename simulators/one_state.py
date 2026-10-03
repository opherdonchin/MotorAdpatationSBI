"""Simulator, Prior Sampler and Schedule Generator of the one-state Model.

Terms (Sitting, Schedule, Block, ...): docs/glossary.md. The Model, its Prior and the
Schedule Design: decision 0005 and docs/models/one_state.md. Parameter order everywhere:
theta = (A, B, sigma_eta, sigma_epsilon).
"""

import numpy as np
from scipy.special import expit

# The four kinds of Block, in this order: perturbation p and vision flag v of each.
BLOCK_KINDS = ("baseline", "+1", "-1", "no vision")
BLOCK_P = np.array([0.0, 1.0, -1.0, 0.0])
BLOCK_V = np.array([1, 1, 1, 0])


def simulate_sitting(rng, theta, p, v, size=()):
    """Simulator: the movement angles of one or more Sittings on a given Schedule.

    Runs the Model of decision 0005 forward, one Trial at a time::

        x[0] ~ N(0, sigma_eta^2)
        y[t] = x[t] + epsilon[t],                 epsilon[t] ~ N(0, sigma_epsilon^2)
        e[t] = y[t] + p[t]
        x[t+1] = A x[t] - B v[t] e[t] + eta[t],   eta[t] ~ N(0, sigma_eta^2)

    Several Sittings that share the parameter values and the Schedule are simulated at
    once (vectorized over `size`); the loop over Trials is the Model's recursion. The
    hidden plans x are not returned, so the Ground Truth is theta alone.

    Parameters
    ----------
    rng : numpy.random.Generator
        Source of all the noise. It is advanced by the draws (the only side effect).
    theta : array_like of float, shape (4,)
        Parameters (A, B, sigma_eta, sigma_epsilon): retention and adaptation rate,
        each strictly between 0 and 1, and the standard deviations of the planning
        and execution noise, each positive. In units of the perturbation size.
    p : array_like of float, shape (T,)
        Perturbation on each Trial, added to the movement to give the error.
    v : array_like of {0, 1}, shape (T,)
        Vision flag on each Trial: 1 if the cursor is shown, so the subject learns from
        the error; 0 if not, so the plan only decays and picks up planning noise.
    size : tuple of int, optional
        Number of independent Sittings to simulate, as an array shape. Default ``()``:
        one Sitting.

    Returns
    -------
    y : numpy.ndarray of float, shape (*size, T)
        Movement angle on every Trial of every Sitting.

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
    """Prior Sampler: draw parameter vectors from the Prior of decision 0005.

    Each part of the Prior is normal on an unbounded scale and is then transformed::

        A             = expit(N(mu_logit_A, sigma_logit_A))
        B             = expit(N(mu_logit_B, sigma_logit_B))
        sigma_epsilon = exp(N(mu_log_sigma_epsilon, sigma_log_sigma_epsilon))
        sigma_eta     = sigma_epsilon * exp(N(mu_log_ratio, sigma_log_ratio))

    so the planning noise is given a Prior through its ratio to the execution noise.
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
    """Schedule Generator: draw the Schedule of one Sitting.

    A Schedule is the Condition on every Trial, here the perturbation and the vision
    flag. Following the Schedule Design of decision 0005: the number of Blocks is
    uniform on n_blocks_min..n_blocks_max; Block lengths are independent and
    log-normal, rounded to whole Trials; the Sitting's proportions of the four kinds of
    Block (`BLOCK_KINDS`) are drawn from a symmetric Dirichlet with the given
    concentration; the first Block is a baseline and every later Block's kind is drawn
    independently with those proportions. Two neighbouring Blocks of the same kind are,
    in effect, one longer Block. The Blocks themselves are not returned: they are part
    of the Schedule Design, not of the Schedule.

    Parameters
    ----------
    rng : numpy.random.Generator
        Source of the draws. It is advanced (the only side effect).
    n_blocks_min, n_blocks_max : int
        Smallest and largest number of Blocks, both included; 1 <= min <= max.
    mu_log_block_len, sigma_log_block_len : float
        Mean and standard deviation of the log of a Block's length in Trials.
    kind_concentration : float
        Concentration of the symmetric Dirichlet over the four kinds, for each kind.
        Larger values make the four proportions more alike.

    Returns
    -------
    p : numpy.ndarray of float, shape (T,)
        Perturbation on each Trial: 0, +1 or -1 (0 on no-vision Trials).
    v : numpy.ndarray of int, shape (T,)
        Vision flag on each Trial: 1, or 0 in no-vision Blocks.

    Raises
    ------
    ValueError
        If the Block counts do not satisfy 1 <= n_blocks_min <= n_blocks_max.
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
