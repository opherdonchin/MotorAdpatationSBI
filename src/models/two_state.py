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
PARAMETERS = ("Af", "As", "Bf", "Bs", "s_eta", "s_epsilon")


def simulate_sitting(rng, theta, schedule, size=()):
    """Simulator: one or more Sittings on a given Schedule, and their Ground Truth.

    Runs the Model of decision 0008 forward, one Trial at a time. The plan has a fast
    and a slow part, which learn from the same error::

        x_fast[0], x_slow[0] ~ N(0, s_eta^2)
        y[t] = x_fast[t] + x_slow[t] + p[t] + epsilon[t],   epsilon[t] ~ N(0, s_epsilon^2)
        x_fast[t+1] = Af x_fast[t] - Bf v[t] y[t] + eta_fast[t]
        x_slow[t+1] = As x_slow[t] - Bs v[t] y[t] + eta_slow[t]

    with eta_fast[t] and eta_slow[t] independent, each N(0, s_eta^2). The observed y is
    the error (where the cursor went relative to the target), not the movement; the
    movement is y - p. This differs from the one-state Model until issue #34. Several
    Sittings that share the parameter values and the Schedule are simulated at once
    (vectorized over `size`); the loop over Trials is the Model's recursion.

    Parameters
    ----------
    rng : numpy.random.Generator
        Source of all the noise. It is advanced by the draws (the only side effect).
    theta : array_like of float, shape (6,)
        Parameter values, in the order of `PARAMETERS`: retention of the fast and of
        the slow state and adaptation rate of the fast and of the slow state, each
        strictly between 0 and 1, with ``Af < As`` and ``Bf > Bs``;
        then the standard deviations of the planning noise (of each state) and of the
        execution noise, each positive. In units of the perturbation size.
    schedule : dict
        The Schedule: one array of shape (T,) per name in the Task's
        `CONDITION_VARS`, and no others. ``schedule["p"]`` is the perturbation on each
        Trial, added to the plan and the execution noise to give the error. ``schedule["v"]`` is the vision
        flag on each Trial, 0 or 1: 1 if the cursor is shown, so both states learn from
        the error; 0 if not, so each state only decays and picks up planning noise.
    size : tuple of int, optional
        Number of independent Sittings to simulate, as an array shape. Default ``()``:
        one Sitting.

    Returns
    -------
    observations : dict
        One array per name in the Task's `OBSERVATION_VARS`: ``"y"``, the error
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
    Af, As, Bf, Bs, s_eta, s_epsilon = theta
    if not np.all((theta[:4] > 0) & (theta[:4] < 1)):
        raise ValueError(
            "Af, As, Bf and Bs must be strictly between 0 and 1, got "
            f"Af={Af}, As={As}, Bf={Bf}, Bs={Bs}"
        )
    if not (Af < As and Bf > Bs):
        raise ValueError(
            "the states must be ordered, Af < As and Bf > Bs, got "
            f"Af={Af}, As={As}, Bf={Bf}, Bs={Bs}"
        )
    if not (s_eta > 0 and s_epsilon > 0):
        raise ValueError(
            "s_eta and s_epsilon must be positive, got "
            f"s_eta={s_eta}, s_epsilon={s_epsilon}"
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
    plan_fast = rng.normal(0.0, s_eta, size)  # the first plan, fast part
    plan_slow = rng.normal(0.0, s_eta, size)  # the first plan, slow part
    for t in range(len(p)):
        x_fast[..., t] = plan_fast
        x_slow[..., t] = plan_slow
        y[..., t] = plan_fast + plan_slow + p[t] + rng.normal(0.0, s_epsilon, size)
        plan_fast = (
            Af * plan_fast - Bf * v[t] * y[..., t] + rng.normal(0.0, s_eta, size)
        )
        plan_slow = (
            As * plan_slow - Bs * v[t] * y[..., t] + rng.normal(0.0, s_eta, size)
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

        logit_Af  = N(mu_logit_Af, sigma_logit_Af)
        logit_Bf  = N(mu_logit_Bf, sigma_logit_Bf)
        d_A       = exp(N(mu_log_d_A, sigma_log_d_A))
        d_B       = exp(N(mu_log_d_B, sigma_log_d_B))
        Af        = special.expit(logit_Af)
        As        = special.expit(logit_Af + d_A)
        Bf        = special.expit(logit_Bf)
        Bs        = special.expit(logit_Bf - d_B)
        s_epsilon = exp(N(mu_log_s_epsilon, sigma_log_s_epsilon))
        s_eta     = s_epsilon * exp(N(mu_log_ratio, sigma_log_ratio))

    The six normal draws are independent.

    Parameters
    ----------
    rng : numpy.random.Generator
        Source of the draws. It is advanced (the only side effect).
    size : int
        Number of parameter vectors to draw.
    prior : dict of float
        The Prior's constants, exactly these keys: ``mu_logit_Af`` and
        ``sigma_logit_Af`` (mean and standard deviation of logit(Af));
        ``mu_log_d_A`` and ``sigma_log_d_A`` (of the log of
        logit(As) - logit(Af)); ``mu_logit_Bf`` and ``sigma_logit_Bf`` (of logit(Bf));
        ``mu_log_d_B`` and ``sigma_log_d_B`` (of the log of
        logit(Bf) - logit(Bs)); ``mu_log_s_epsilon`` and ``sigma_log_s_epsilon`` (of
        log(s_epsilon)); ``mu_log_ratio`` and ``sigma_log_ratio`` (of
        log(s_eta / s_epsilon)).

    Returns
    -------
    theta : numpy.ndarray of float, shape (size, 6)
        Columns in the order of `PARAMETERS`, as `simulate_sitting` takes them. Every
        row has ``Af < As`` and ``Bf > Bs``.

    Raises
    ------
    ValueError
        If `prior` does not have exactly the keys listed above.
    """
    keys = {
        "mu_logit_Af",
        "sigma_logit_Af",
        "mu_log_d_A",
        "sigma_log_d_A",
        "mu_logit_Bf",
        "sigma_logit_Bf",
        "mu_log_d_B",
        "sigma_log_d_B",
        "mu_log_s_epsilon",
        "sigma_log_s_epsilon",
        "mu_log_ratio",
        "sigma_log_ratio",
    }
    if set(prior) != keys:
        raise ValueError(
            f"prior must have exactly the keys {sorted(keys)}, got {sorted(prior)}"
        )
    logit_Af = rng.normal(prior["mu_logit_Af"], prior["sigma_logit_Af"], size)
    d_A = np.exp(rng.normal(prior["mu_log_d_A"], prior["sigma_log_d_A"], size))
    logit_Bf = rng.normal(prior["mu_logit_Bf"], prior["sigma_logit_Bf"], size)
    d_B = np.exp(rng.normal(prior["mu_log_d_B"], prior["sigma_log_d_B"], size))
    log_s_epsilon = rng.normal(
        prior["mu_log_s_epsilon"], prior["sigma_log_s_epsilon"], size
    )
    log_ratio = rng.normal(prior["mu_log_ratio"], prior["sigma_log_ratio"], size)
    Af = special.expit(logit_Af)
    As = special.expit(logit_Af + d_A)
    Bf = special.expit(logit_Bf)
    Bs = special.expit(logit_Bf - d_B)
    s_epsilon = np.exp(log_s_epsilon)
    s_eta = np.exp(log_s_epsilon + log_ratio)
    return np.column_stack([Af, As, Bf, Bs, s_eta, s_epsilon])
