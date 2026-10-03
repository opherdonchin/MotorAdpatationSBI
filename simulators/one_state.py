"""Simulator, Prior Sampler and Schedule Generator of the one-state Model.

Terms (Sitting, Schedule, Block, ...): docs/glossary.md. The Model, its Prior and the
Schedule Design: decision 0005 and docs/models/one_state.md. Parameter order everywhere:
theta = (A, B, sigma_eta, sigma_epsilon).
"""

from types import MappingProxyType

import numpy as np
from scipy.special import expit

# The Model's contract: the parameters in theta (in this order), the Conditions it needs
# on every Trial, and what it produces on every Trial.
PARAMETER_NAMES = ("A", "B", "sigma_eta", "sigma_epsilon")
CONDITION_NAMES = ("p", "v")
OBSERVATION_NAMES = ("y",)

# The Trial Types of the Schedule Design (decision 0005), with their Conditions.
TRIAL_TYPES = MappingProxyType(
    {
        "baseline": {"p": 0.0, "v": 1},
        "+1": {"p": 1.0, "v": 1},
        "-1": {"p": -1.0, "v": 1},
        "no vision": {"p": 0.0, "v": 0},
    }
)


def simulate_sitting(rng, theta, schedule, size=()):
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
        Parameter values, in the order of `PARAMETER_NAMES`: retention and adaptation
        rate, each strictly between 0 and 1, and the standard deviations of the
        planning and execution noise, each positive. In units of the perturbation size.
    schedule : dict
        The Schedule: one array of shape (T,) per name in `CONDITION_NAMES`, and no
        others. ``schedule["p"]`` is the perturbation on each Trial, added to the
        movement to give the error. ``schedule["v"]`` is the vision flag on each Trial,
        0 or 1: 1 if the cursor is shown, so the subject learns from the error; 0 if
        not, so the plan only decays and picks up planning noise.
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
        If theta does not have shape (4,), a parameter is outside its domain, the
        Schedule does not have exactly the keys in `CONDITION_NAMES`, its arrays are not
        one-dimensional or differ in length, or v holds values other than 0 and 1.
    """
    if set(schedule) != set(CONDITION_NAMES):
        raise ValueError(
            f"schedule must have exactly the keys {CONDITION_NAMES}, "
            f"got {tuple(schedule)}"
        )
    theta = np.asarray(theta, dtype=float)
    p = np.asarray(schedule["p"], dtype=float)
    v = np.asarray(schedule["v"])
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


def sample_prior(rng, size, prior):
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
    prior : dict of float
        The Prior's constants, exactly these keys: ``mu_logit_A`` and ``sigma_logit_A``
        (mean and standard deviation of logit(A)); ``mu_logit_B`` and ``sigma_logit_B``
        (of logit(B)); ``mu_log_sigma_epsilon`` and ``sigma_log_sigma_epsilon`` (of
        log(sigma_epsilon)); ``mu_log_ratio`` and ``sigma_log_ratio`` (of
        log(sigma_eta / sigma_epsilon)).

    Returns
    -------
    theta : numpy.ndarray of float, shape (size, 4)
        Columns in the order of `PARAMETER_NAMES`, as `simulate_sitting` takes them.

    Raises
    ------
    ValueError
        If `prior` does not have exactly the keys listed above.
    """
    keys = {
        "mu_logit_A",
        "sigma_logit_A",
        "mu_logit_B",
        "sigma_logit_B",
        "mu_log_sigma_epsilon",
        "sigma_log_sigma_epsilon",
        "mu_log_ratio",
        "sigma_log_ratio",
    }
    if set(prior) != keys:
        raise ValueError(
            f"prior must have exactly the keys {sorted(keys)}, got {sorted(prior)}"
        )
    A = expit(rng.normal(prior["mu_logit_A"], prior["sigma_logit_A"], size))
    B = expit(rng.normal(prior["mu_logit_B"], prior["sigma_logit_B"], size))
    log_sigma_epsilon = rng.normal(
        prior["mu_log_sigma_epsilon"], prior["sigma_log_sigma_epsilon"], size
    )
    log_ratio = rng.normal(prior["mu_log_ratio"], prior["sigma_log_ratio"], size)
    sigma_epsilon = np.exp(log_sigma_epsilon)
    sigma_eta = np.exp(log_sigma_epsilon + log_ratio)
    return np.column_stack([A, B, sigma_eta, sigma_epsilon])


def sample_schedule(rng, schedule_design):
    """Schedule Generator: draw the Schedule of one Sitting.

    A Schedule is the Condition on every Trial, here the perturbation and the vision
    flag. Following the Schedule Design of decision 0005, every Block is a run of Trials
    of one Trial Type (`TRIAL_TYPES`): the number of Blocks is uniform on
    n_blocks_min..n_blocks_max; Block lengths are independent and log-normal, rounded
    to whole Trials; the Sitting's proportions of the Trial Types are drawn from a
    symmetric Dirichlet with the given concentration; the first Block is a baseline and
    every later Block's Trial Type is drawn independently with those proportions. Two
    neighbouring Blocks of the same Trial Type are, in effect, one longer Block. The
    Blocks themselves are not returned: they are part of the Schedule Design, not of
    the Schedule.

    Parameters
    ----------
    rng : numpy.random.Generator
        Source of the draws. It is advanced (the only side effect).
    schedule_design : dict
        The Schedule Design's constants, exactly these keys: ``n_blocks_min`` and
        ``n_blocks_max`` (int; smallest and largest number of Blocks, both included,
        1 <= min <= max); ``mu_log_block_len`` and ``sigma_log_block_len`` (float; mean
        and standard deviation of the log of a Block's length in Trials);
        ``trial_type_concentration`` (float; concentration of the symmetric Dirichlet
        over the Trial Types, for each Trial Type; larger values make the proportions
        more alike).

    Returns
    -------
    schedule : dict
        The Schedule, keyed by `CONDITION_NAMES`: ``"p"``, the perturbation on each
        Trial (float, shape (T,): 0, +1 or -1, and 0 on no-vision Trials), and ``"v"``,
        the vision flag on each Trial (int, shape (T,): 1, or 0 in no-vision Blocks).

    Raises
    ------
    ValueError
        If `schedule_design` does not have exactly the keys listed above, or the Block
        counts do not satisfy 1 <= n_blocks_min <= n_blocks_max.
    """
    keys = {
        "n_blocks_min",
        "n_blocks_max",
        "mu_log_block_len",
        "sigma_log_block_len",
        "trial_type_concentration",
    }
    if set(schedule_design) != keys:
        raise ValueError(
            f"schedule_design must have exactly the keys {sorted(keys)}, "
            f"got {sorted(schedule_design)}"
        )
    n_min, n_max = schedule_design["n_blocks_min"], schedule_design["n_blocks_max"]
    if not 1 <= n_min <= n_max:
        raise ValueError(
            f"need 1 <= n_blocks_min <= n_blocks_max, got {n_min} and {n_max}"
        )
    n_blocks = rng.integers(n_min, n_max + 1)
    log_len = rng.normal(
        schedule_design["mu_log_block_len"],
        schedule_design["sigma_log_block_len"],
        n_blocks,
    )
    block_len = np.rint(np.exp(log_len)).astype(int)
    n_types = len(TRIAL_TYPES)
    concentration = np.full(n_types, schedule_design["trial_type_concentration"])
    proportions = rng.dirichlet(concentration)
    later_types = rng.choice(n_types, size=n_blocks - 1, p=proportions)
    block_type = np.concatenate([[0], later_types])  # the first Block is a baseline
    # For each Condition, its value in each Trial Type, then on every Trial.
    by_type = {
        name: np.array([conditions[name] for conditions in TRIAL_TYPES.values()])
        for name in CONDITION_NAMES
    }
    return {
        name: np.repeat(values[block_type], block_len)
        for name, values in by_type.items()
    }
