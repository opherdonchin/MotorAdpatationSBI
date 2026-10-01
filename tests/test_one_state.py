"""Code tests for the one-state model: simulator, schedules, prior and likelihood.

The scientific checks (simulator against the model, recovery, calibration) are in
the notebook; these are fast checks that the code does what its docstrings say.
"""

import numpy as np
import pytensor
import pytensor.tensor as pt
import pytest
from scipy.stats import multivariate_normal

from motor_sbi.one_state import joint_gaussian, kalman_logp
from simulators.one_state import (
    PERTURBATION_VALUES,
    sample_prior,
    sample_schedule,
    simulate_sitting,
)

ROOT_SEED = 76737827330687806742309298008879821606  # secrets.randbits(128)

PRIOR = {
    "mu_logit_A": 4.0,
    "sigma_logit_A": 1.5,
    "mu_logit_B": -2.3,
    "sigma_logit_B": 1.2,
    "mu_log_sigma_y": -1.9,
    "sigma_log_sigma_y": 0.4,
    "mu_log_ratio": -2.2,
    "sigma_log_ratio": 0.3,
}
SCHEDULE = {
    "n_blocks_min": 3,
    "n_blocks_max": 10,
    "mu_log_block_len": 3.1,
    "sigma_log_block_len": 0.4,
}
THETA = np.array([0.95, 0.2, 0.05, 0.15])


@pytest.fixture
def rng():
    return np.random.default_rng(ROOT_SEED)


@pytest.fixture(scope="module")
def kalman_loglik():
    y, p = pt.dvectors("y", "p")
    A, B, sigma_x, sigma_y = pt.dscalars("A", "B", "sigma_x", "sigma_y")
    args = [y, A, B, sigma_x, sigma_y, p]
    return pytensor.function(args, kalman_logp(*args))


def test_prior_draws_have_the_documented_shape_and_domains(rng):
    theta = sample_prior(rng, 1000, **PRIOR)
    A, B, sigma_x, sigma_y = theta.T
    assert theta.shape == (1000, 4)
    assert np.all((A > 0) & (A < 1) & (B > 0) & (B < 1))
    assert np.all((sigma_x > 0) & (sigma_y > 0))


def test_schedules_start_at_baseline_and_change_at_every_boundary(rng):
    for _ in range(200):
        p = sample_schedule(rng, **SCHEDULE)
        assert p[0] == 0.0
        assert np.all(np.isin(p, PERTURBATION_VALUES))
        # Every boundary is a change, so the blocks are exactly the runs of p.
        n_blocks = 1 + np.count_nonzero(np.diff(p))
        assert SCHEDULE["n_blocks_min"] <= n_blocks <= SCHEDULE["n_blocks_max"]


def test_schedule_rejects_an_impossible_block_range(rng):
    with pytest.raises(ValueError, match="n_blocks_min"):
        sample_schedule(rng, **{**SCHEDULE, "n_blocks_min": 0})


def test_simulated_sittings_have_the_requested_shape(rng):
    p = sample_schedule(rng, **SCHEDULE)
    assert simulate_sitting(rng, THETA, p).shape == (len(p),)
    assert simulate_sitting(rng, THETA, p, size=(7,)).shape == (7, len(p))


def test_simulator_is_reproducible_from_its_generator():
    p = np.repeat(PERTURBATION_VALUES, 5)
    y1 = simulate_sitting(np.random.default_rng(ROOT_SEED), THETA, p)
    y2 = simulate_sitting(np.random.default_rng(ROOT_SEED), THETA, p)
    np.testing.assert_array_equal(y1, y2)


@pytest.mark.parametrize(
    "theta, message",
    [
        ([0.95, 0.2, 0.05], "shape"),
        ([1.0, 0.2, 0.05, 0.15], "A and B"),
        ([0.95, 0.0, 0.05, 0.15], "A and B"),
        ([0.95, 0.2, 0.0, 0.15], "positive"),
        ([0.95, 0.2, 0.05, -0.1], "positive"),
    ],
)
def test_simulator_rejects_invalid_parameters(rng, theta, message):
    with pytest.raises(ValueError, match=message):
        simulate_sitting(rng, theta, np.zeros(5))


def test_simulator_rejects_a_schedule_that_is_not_a_vector(rng):
    with pytest.raises(ValueError, match="one-dimensional"):
        simulate_sitting(rng, THETA, np.zeros((2, 5)))


def test_noise_free_limit_follows_the_deterministic_learning_curve(rng):
    # With negligible noise, y_t = x_t and x_{t+1} = (A - B) x_t + B p_t.
    A, B = 0.95, 0.2
    p = np.repeat([0.0, 1.0], 20)
    y = simulate_sitting(rng, [A, B, 1e-12, 1e-12], p)
    x = np.zeros(len(p))
    for t in range(len(p) - 1):
        x[t + 1] = (A - B) * x[t] + B * p[t]
    np.testing.assert_allclose(y, x, atol=1e-9)


def test_kalman_filter_matches_the_joint_gaussian(rng, kalman_loglik):
    for theta in sample_prior(rng, 10, **PRIOR):
        p = rng.choice(PERTURBATION_VALUES, 8)
        y = simulate_sitting(rng, THETA, p)  # data from other parameters
        mean, cov = joint_gaussian(theta, p)
        expected = multivariate_normal(mean, cov).logpdf(y)
        np.testing.assert_allclose(kalman_loglik(y, *theta, p), expected, rtol=1e-9)


def test_joint_gaussian_of_one_trial_is_state_plus_output_noise():
    mean, cov = joint_gaussian(THETA, np.zeros(1))
    np.testing.assert_allclose(mean, [0.0])
    np.testing.assert_allclose(cov, [[THETA[2] ** 2 + THETA[3] ** 2]])
