"""One-state motor-adaptation model: prior, perturbation schedules and simulator.

Math and parameter meanings: docs/models/one_state.md.
Parameter order everywhere: theta = (A, B, sigma_x, sigma_y).
"""

import numpy as np
from scipy.special import expit

# "Move to one of the other two values" is a step of 1 or 2 positions around this list.
PERTURBATION_VALUES = np.array([0.0, 1.0, -1.0])


def sample_prior(
    rng,
    size,
    *,
    mu_logit_A,
    sigma_logit_A,
    mu_logit_B,
    sigma_logit_B,
    mu_log_sigma_y,
    sigma_log_sigma_y,
    mu_log_ratio,
    sigma_log_ratio,
):
    """Draw `size` parameter vectors from the prior.

    Each prior is normal on an unbounded scale; `ratio` is sigma_x / sigma_y.
    Returns theta with shape (size, 4), columns (A, B, sigma_x, sigma_y).
    """
    A = expit(rng.normal(mu_logit_A, sigma_logit_A, size))
    B = expit(rng.normal(mu_logit_B, sigma_logit_B, size))
    sigma_y = np.exp(rng.normal(mu_log_sigma_y, sigma_log_sigma_y, size))
    sigma_x = sigma_y * np.exp(rng.normal(mu_log_ratio, sigma_log_ratio, size))
    return np.column_stack([A, B, sigma_x, sigma_y])


def sample_schedule(
    rng, *, n_blocks_min, n_blocks_max, mu_log_block_len, sigma_log_block_len
):
    """Draw the perturbation schedule of one sitting.

    The number of blocks is uniform on n_blocks_min..n_blocks_max. The first block is a
    baseline (0); at each boundary the perturbation moves to one of the other two
    values. Block lengths are log-normal, rounded to whole trials.
    Returns p with shape (T,).
    """
    if not 1 <= n_blocks_min <= n_blocks_max:
        raise ValueError(
            "need 1 <= n_blocks_min <= n_blocks_max, got "
            f"n_blocks_min={n_blocks_min}, n_blocks_max={n_blocks_max}"
        )
    n_blocks = rng.integers(n_blocks_min, n_blocks_max + 1)
    log_block_len = rng.normal(mu_log_block_len, sigma_log_block_len, n_blocks)
    block_len = np.rint(np.exp(log_block_len)).astype(int)
    steps = rng.integers(1, 3, n_blocks - 1)  # 1 or 2: always a change
    position = np.concatenate([[0], np.cumsum(steps)]) % 3  # first block is baseline
    return np.repeat(PERTURBATION_VALUES[position], block_len)


def simulate_sitting(rng, theta, p, size=()):
    """Simulate the responses of `size` independent sittings sharing theta and p.

    The loop over trials is the model's recursion; sittings are vectorized.
    Returns y with shape (*size, T).
    """
    theta = np.asarray(theta, dtype=float)
    p = np.asarray(p, dtype=float)
    if theta.shape != (4,):
        raise ValueError(f"theta must have shape (4,), got {theta.shape}")
    if p.ndim != 1:
        raise ValueError(f"p must be one-dimensional, got shape {p.shape}")
    A, B, sigma_x, sigma_y = theta
    if not (0 < A < 1 and 0 < B < 1):
        raise ValueError(f"A and B must be in (0, 1), got A={A}, B={B}")
    if not (sigma_x > 0 and sigma_y > 0):
        raise ValueError(
            f"sigma_x and sigma_y must be positive, got {sigma_x}, {sigma_y}"
        )

    y = np.empty((*size, len(p)))
    x = rng.normal(0.0, sigma_x, size)  # x_1
    for t in range(len(p)):
        y[..., t] = x + rng.normal(0.0, sigma_y, size)
        x = A * x + B * (p[t] - y[..., t]) + rng.normal(0.0, sigma_x, size)
    return y
