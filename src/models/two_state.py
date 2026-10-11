"""The two-state Model: its parameters, Prior Sampler and Simulator.

The Model and its Prior: decision 0008 and docs/models/two_state.md. Terms:
docs/glossary.md; where this module fits: decision 0006.
"""

import numpy as np
from scipy import special

from designs import visuomotor_adaptation_task as tsk

# The Task this Model is written for: its Schedules hold TASK.CONDITION_VARS and its
# Sittings TASK.OBSERVATION_VARS.
TASK = tsk

# The Model's parameters, in the order they have in a parameter vector theta.
PARAMETERS = ("A_fast", "A_slow", "B_fast", "B_slow", "sigma_eta", "sigma_epsilon")


def simulate_sitting(rng, theta, schedule, size=()):
    """Simulator: one or more Sittings on a given Schedule, and their Ground Truth.

    Runs the Model of decision 0008 forward, one Trial at a time. The plan has a fast
    and a slow part, which learn from the same error::

        x_fast[0], x_slow[0] ~ N(0, sigma_eta^2)
        y[t] = x_fast[t] + x_slow[t] + epsilon[t],   epsilon[t] ~ N(0, sigma_epsilon^2)
        e[t] = y[t] + p[t]
        x_fast[t+1] = A_fast x_fast[t] - B_fast v[t] e[t] + eta_fast[t]
        x_slow[t+1] = A_slow x_slow[t] - B_slow v[t] e[t] + eta_slow[t]

    with eta_fast[t] and eta_slow[t] independent, each N(0, sigma_eta^2). Several
    Sittings that share the parameter values and the Schedule are simulated at once
    (vectorized over `size`); the loop over Trials is the Model's recursion.

    Parameters
    ----------
    rng : numpy.random.Generator
        Source of all the noise. It is advanced by the draws (the only side effect).
    theta : array_like of float, shape (6,)
        Parameter values, in the order of `PARAMETERS`: retention of the fast and of
        the slow state and adaptation rate of the fast and of the slow state, each
        strictly between 0 and 1, with ``A_fast < A_slow`` and ``B_fast > B_slow``;
        then the standard deviations of the planning noise (of each state) and of the
        execution noise, each positive. In units of the perturbation size.
    schedule : dict
        The Schedule: one array of shape (T,) per name in the Task's
        `CONDITION_VARS`, and no others. ``schedule["p"]`` is the perturbation on each
        Trial, added to the movement to give the error. ``schedule["v"]`` is the vision
        flag on each Trial, 0 or 1: 1 if the cursor is shown, so both states learn from
        the error; 0 if not, so each state only decays and picks up planning noise.
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
        per name in `PARAMETERS`, and ``"x_fast"`` and ``"x_slow"``, the two hidden
        parts of the plan on every Trial (float, shape (*size, T) each).

    Raises
    ------
    ValueError
        If theta does not have shape (6,), a parameter is outside its domain, the two
        states are not ordered as fast and slow, the Schedule does not have exactly the
        keys in `CONDITION_VARS`, its arrays are not one-dimensional or differ in
        length, or v holds values other than 0 and 1.
    """
    if set(schedule) != set(TASK.CONDITION_VARS):
        raise ValueError(
            f"schedule must have exactly the keys {TASK.CONDITION_VARS}, "
            f"got {tuple(schedule)}"
        )
    theta = np.asarray(theta, dtype=float)
    p = np.asarray(schedule["p"], dtype=float)
    v = np.asarray(schedule["v"])
    if theta.shape != (6,):
        raise ValueError(f"theta must have shape (6,), got {theta.shape}")
    A_fast, A_slow, B_fast, B_slow, sigma_eta, sigma_epsilon = theta
    if not np.all((theta[:4] > 0) & (theta[:4] < 1)):
        raise ValueError(
            "A_fast, A_slow, B_fast and B_slow must be strictly between 0 and 1, got "
            f"A_fast={A_fast}, A_slow={A_slow}, B_fast={B_fast}, B_slow={B_slow}"
        )
    if not (A_fast < A_slow and B_fast > B_slow):
        raise ValueError(
            "the states must be ordered, A_fast < A_slow and B_fast > B_slow, got "
            f"A_fast={A_fast}, A_slow={A_slow}, B_fast={B_fast}, B_slow={B_slow}"
        )
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

    x_fast = np.empty((*size, len(p)))
    x_slow = np.empty((*size, len(p)))
    y = np.empty((*size, len(p)))
    plan_fast = rng.normal(0.0, sigma_eta, size)  # the first plan, fast part
    plan_slow = rng.normal(0.0, sigma_eta, size)  # the first plan, slow part
    for t in range(len(p)):
        x_fast[..., t] = plan_fast
        x_slow[..., t] = plan_slow
        y[..., t] = plan_fast + plan_slow + rng.normal(0.0, sigma_epsilon, size)
        e = y[..., t] + p[t]
        plan_fast = (
            A_fast * plan_fast - B_fast * v[t] * e + rng.normal(0.0, sigma_eta, size)
        )
        plan_slow = (
            A_slow * plan_slow - B_slow * v[t] * e + rng.normal(0.0, sigma_eta, size)
        )
    ground_truth = {
        **dict(zip(PARAMETERS, theta.tolist())),
        "x_fast": x_fast,
        "x_slow": x_slow,
    }
    return {"y": y}, ground_truth


def sample_prior(rng, size, prior):
    """Prior Sampler: draw parameter vectors from the Prior of decision 0008.

    Each part of the Prior is normal on an unbounded scale and is then transformed.
    The fast state's rates are drawn on the logit scale, and each slow rate is the fast
    one moved by a positive difference on that scale, so the states are ordered by
    construction::

        logit_A_fast  = N(mu_logit_A_fast, sigma_logit_A_fast)
        logit_B_fast  = N(mu_logit_B_fast, sigma_logit_B_fast)
        A_fast        = special.expit(logit_A_fast)
        A_slow        = special.expit(logit_A_fast + exp(N(mu_log_A_diff, sigma_log_A_diff)))
        B_fast        = special.expit(logit_B_fast)
        B_slow        = special.expit(logit_B_fast - exp(N(mu_log_B_diff, sigma_log_B_diff)))
        sigma_epsilon = exp(N(mu_log_sigma_epsilon, sigma_log_sigma_epsilon))
        sigma_eta     = sigma_epsilon * exp(N(mu_log_ratio, sigma_log_ratio))

    The six normal draws are independent. The Prior is truncated to the region where
    the Model is stable, ``B_fast / (1 + A_fast) + B_slow / (1 + A_slow) < 1``: a draw
    outside it is discarded and drawn again, all six parts together.

    Parameters
    ----------
    rng : numpy.random.Generator
        Source of the draws. It is advanced (the only side effect), by more draws when
        some are discarded.
    size : int
        Number of parameter vectors to draw.
    prior : dict of float
        The Prior's constants, exactly these keys: ``mu_logit_A_fast`` and
        ``sigma_logit_A_fast`` (mean and standard deviation of logit(A_fast));
        ``mu_log_A_diff`` and ``sigma_log_A_diff`` (of the log of
        logit(A_slow) - logit(A_fast)); ``mu_logit_B_fast`` and ``sigma_logit_B_fast``
        (of logit(B_fast)); ``mu_log_B_diff`` and ``sigma_log_B_diff`` (of the log of
        logit(B_fast) - logit(B_slow)); ``mu_log_sigma_epsilon`` and
        ``sigma_log_sigma_epsilon`` (of log(sigma_epsilon)); ``mu_log_ratio`` and
        ``sigma_log_ratio`` (of log(sigma_eta / sigma_epsilon)).

    Returns
    -------
    theta : numpy.ndarray of float, shape (size, 6)
        Columns in the order of `PARAMETERS`, as `simulate_sitting` takes them. Every
        row is stable and has ``A_fast < A_slow`` and ``B_fast > B_slow``.

    Raises
    ------
    ValueError
        If `prior` does not have exactly the keys listed above.
    """
    keys = {
        "mu_logit_A_fast",
        "sigma_logit_A_fast",
        "mu_log_A_diff",
        "sigma_log_A_diff",
        "mu_logit_B_fast",
        "sigma_logit_B_fast",
        "mu_log_B_diff",
        "sigma_log_B_diff",
        "mu_log_sigma_epsilon",
        "sigma_log_sigma_epsilon",
        "mu_log_ratio",
        "sigma_log_ratio",
    }
    if set(prior) != keys:
        raise ValueError(
            f"prior must have exactly the keys {sorted(keys)}, got {sorted(prior)}"
        )
    theta = np.empty((size, 6))
    todo = np.arange(size)  # rows still to be drawn: all, then those found unstable
    while len(todo) > 0:
        n = len(todo)
        logit_A_fast = rng.normal(
            prior["mu_logit_A_fast"], prior["sigma_logit_A_fast"], n
        )
        A_diff = np.exp(
            rng.normal(prior["mu_log_A_diff"], prior["sigma_log_A_diff"], n)
        )
        logit_B_fast = rng.normal(
            prior["mu_logit_B_fast"], prior["sigma_logit_B_fast"], n
        )
        B_diff = np.exp(
            rng.normal(prior["mu_log_B_diff"], prior["sigma_log_B_diff"], n)
        )
        log_sigma_epsilon = rng.normal(
            prior["mu_log_sigma_epsilon"], prior["sigma_log_sigma_epsilon"], n
        )
        log_ratio = rng.normal(prior["mu_log_ratio"], prior["sigma_log_ratio"], n)
        A_fast = special.expit(logit_A_fast)
        A_slow = special.expit(logit_A_fast + A_diff)
        B_fast = special.expit(logit_B_fast)
        B_slow = special.expit(logit_B_fast - B_diff)
        sigma_epsilon = np.exp(log_sigma_epsilon)
        sigma_eta = np.exp(log_sigma_epsilon + log_ratio)
        theta[todo] = np.column_stack(
            [A_fast, A_slow, B_fast, B_slow, sigma_eta, sigma_epsilon]
        )
        stable = B_fast / (1 + A_fast) + B_slow / (1 + A_slow) < 1
        todo = todo[~stable]
    return theta
