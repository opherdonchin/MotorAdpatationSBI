"""The one-state Model: its parameters, Prior Sampler and Simulator.

The Model and its Prior: decision 0005 and docs/models/one_state.md. Terms:
docs/glossary.md; where this module fits: decision 0006.
"""

import numpy as np
from scipy import special

from designs import visuomotor_adaptation_task as tsk

# The Task this Model is written for: its Schedules hold TASK.CONDITION_VARS and its
# Sittings TASK.OBSERVATION_VARS.
TASK = tsk

# The Model's parameters, in the order they have in a parameter vector theta.
PARAMETERS = ("A", "B", "sigma_eta", "sigma_epsilon")


def simulate_sitting(rng, theta, schedule, size=()):
    """Simulator: one or more Sittings on a given Schedule, and their Ground Truth.

    Runs the Model of decision 0005 forward, one Trial at a time::

        x[0] ~ N(0, sigma_eta^2)
        y[t] = x[t] + epsilon[t],                 epsilon[t] ~ N(0, sigma_epsilon^2)
        e[t] = y[t] + p[t]
        x[t+1] = A x[t] - B v[t] e[t] + eta[t],   eta[t] ~ N(0, sigma_eta^2)

    Several Sittings that share the parameter values and the Schedule are simulated at
    once (vectorized over `size`); the loop over Trials is the Model's recursion.

    Parameters
    ----------
    rng : numpy.random.Generator
        Source of all the noise. It is advanced by the draws (the only side effect).
    theta : array_like of float, shape (4,)
        Parameter values, in the order of `PARAMETERS`: retention and adaptation
        rate, each strictly between 0 and 1, and the standard deviations of the
        planning and execution noise, each positive. In units of the perturbation size.
    schedule : dict
        The Schedule: one array of shape (T,) per name in the Task's
        `CONDITION_VARS`, and no others. ``schedule["p"]`` is the perturbation on each Trial, added to the
        movement to give the error. ``schedule["v"]`` is the vision flag on each Trial,
        0 or 1: 1 if the cursor is shown, so the subject learns from the error; 0 if
        not, so the plan only decays and picks up planning noise.
    size : tuple of int, optional
        Number of independent Sittings to simulate, as an array shape. Default ``()``:
        one Sitting.

    Returns
    -------
    observations : dict
        One array per name in the Task's `OBSERVATION_VARS`: ``"y"``, the movement angle
        on every Trial of every Sitting (float, shape (*size, T)). Together with the
        Schedule, this is the Sitting.
    ground_truth : dict
        What produced the Sittings and is not observed: the parameter values, one float
        per name in `PARAMETERS`, and ``"x"``, the hidden plan on every Trial (float,
        shape (*size, T)).

    Raises
    ------
    ValueError
        If theta does not have shape (4,), a parameter is outside its domain, the
        Schedule does not have exactly the keys in `CONDITION_VARS`, its arrays are not
        one-dimensional or differ in length, or v holds values other than 0 and 1.
    """
    if set(schedule) != set(TASK.CONDITION_VARS):
        raise ValueError(
            f"schedule must have exactly the keys {TASK.CONDITION_VARS}, "
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

    x = np.empty((*size, len(p)))
    y = np.empty((*size, len(p)))
    plan = rng.normal(0.0, sigma_eta, size)  # the first plan
    for t in range(len(p)):
        x[..., t] = plan
        y[..., t] = plan + rng.normal(0.0, sigma_epsilon, size)
        e = y[..., t] + p[t]
        plan = A * plan - B * v[t] * e + rng.normal(0.0, sigma_eta, size)
    ground_truth = {**dict(zip(PARAMETERS, theta.tolist())), "x": x}
    return {"y": y}, ground_truth


def sample_prior(rng, size, prior):
    """Prior Sampler: draw parameter vectors from the Prior of decision 0005.

    Each part of the Prior is normal on an unbounded scale and is then transformed::

        A             = special.expit(N(mu_logit_A, sigma_logit_A))
        B             = special.expit(N(mu_logit_B, sigma_logit_B))
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
        Columns in the order of `PARAMETERS`, as `simulate_sitting` takes them.

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
    A = special.expit(rng.normal(prior["mu_logit_A"], prior["sigma_logit_A"], size))
    B = special.expit(rng.normal(prior["mu_logit_B"], prior["sigma_logit_B"], size))
    log_sigma_epsilon = rng.normal(
        prior["mu_log_sigma_epsilon"], prior["sigma_log_sigma_epsilon"], size
    )
    log_ratio = rng.normal(prior["mu_log_ratio"], prior["sigma_log_ratio"], size)
    sigma_epsilon = np.exp(log_sigma_epsilon)
    sigma_eta = np.exp(log_sigma_epsilon + log_ratio)
    return np.column_stack([A, B, sigma_eta, sigma_epsilon])
