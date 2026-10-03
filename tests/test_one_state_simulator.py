"""Code tests for simulators/one_state.py: Simulator, Prior Sampler, Schedule Generator.

The scientific checks are in notebooks/one_state_simulator.ipynb (the simulator) and
notebooks/one_state_priors.ipynb (Prior and Schedule Design); these are fast checks that the
functions do what their docstrings say.
"""

import numpy as np
import pytest

from simulators.one_state import (
    BLOCK_P,
    BLOCK_V,
    sample_prior,
    sample_schedule,
    simulate_sitting,
)

ROOT_SEED = 68921609159653578200335664192142966917  # secrets.randbits(128)

THETA = np.array([0.95, 0.2, 0.05, 0.15])  # A, B, sigma_eta, sigma_epsilon
PRIOR = {
    "mu_logit_A": 4.0,
    "sigma_logit_A": 1.5,
    "mu_logit_B": -2.3,
    "sigma_logit_B": 1.2,
    "mu_log_sigma_epsilon": -1.9,
    "sigma_log_sigma_epsilon": 0.4,
    "mu_log_ratio": -2.2,
    "sigma_log_ratio": 0.3,
}
SCHEDULE = {
    "n_blocks_min": 8,
    "n_blocks_max": 60,
    "mu_log_block_len": 3.1,
    "sigma_log_block_len": 0.4,
    "kind_concentration": 3.0,
}
TINY = 1e-12  # noise standard deviation small enough to make a sitting deterministic


@pytest.fixture
def rng():
    return np.random.default_rng(ROOT_SEED)


def test_one_sitting_and_many_sittings_have_the_documented_shapes(rng):
    p, v = np.zeros(30), np.ones(30)
    assert simulate_sitting(rng, THETA, p, v).shape == (30,)
    assert simulate_sitting(rng, THETA, p, v, size=(7,)).shape == (7, 30)
    assert simulate_sitting(rng, THETA, p, v, size=(2, 3)).shape == (2, 3, 30)


def test_the_same_generator_state_gives_the_same_sitting():
    p, v = np.repeat([0.0, 1.0, -1.0], 10), np.ones(30)
    y1 = simulate_sitting(np.random.default_rng(ROOT_SEED), THETA, p, v)
    y2 = simulate_sitting(np.random.default_rng(ROOT_SEED), THETA, p, v)
    np.testing.assert_array_equal(y1, y2)


def test_without_noise_a_learner_moves_to_the_fixed_point_geometrically(rng):
    # With vision and a constant p, y[t+1] - y* = (A - B) (y[t] - y*),
    # where y* = -B p / (1 - A + B).
    A, B = 0.95, 0.2
    p, v = np.ones(40), np.ones(40)
    y = simulate_sitting(rng, [A, B, TINY, TINY], p, v)
    y_star = -B / (1 - A + B)
    expected = y_star + (0.0 - y_star) * (A - B) ** np.arange(40)
    np.testing.assert_allclose(y, expected, atol=1e-9)


def test_without_vision_the_plan_only_decays(rng):
    # Adapt for 30 trials with vision, then 20 trials without: y[t+1] = A y[t].
    A, B = 0.95, 0.2
    p = np.concatenate([np.ones(30), np.ones(20)])
    v = np.concatenate([np.ones(30), np.zeros(20)])
    y = simulate_sitting(rng, [A, B, TINY, TINY], p, v)
    np.testing.assert_allclose(y[31:], A * y[30:-1], atol=1e-9)


@pytest.mark.parametrize(
    "theta, message",
    [
        ([0.95, 0.2, 0.05], "shape"),
        ([1.0, 0.2, 0.05, 0.15], "between 0 and 1"),
        ([0.95, 0.0, 0.05, 0.15], "between 0 and 1"),
        ([0.95, 0.2, 0.0, 0.15], "positive"),
        ([0.95, 0.2, 0.05, -0.1], "positive"),
    ],
)
def test_parameters_outside_their_domain_are_rejected(rng, theta, message):
    with pytest.raises(ValueError, match=message):
        simulate_sitting(rng, theta, np.zeros(5), np.ones(5))


@pytest.mark.parametrize(
    "p, v, message",
    [
        (np.zeros((2, 5)), np.ones(5), "one-dimensional"),
        (np.zeros(5), np.ones((2, 5)), "one-dimensional"),
        (np.zeros(5), np.ones(4), "same length"),
        (np.zeros(5), np.full(5, 0.5), "only 0 and 1"),
    ],
)
def test_malformed_schedules_are_rejected(rng, p, v, message):
    with pytest.raises(ValueError, match=message):
        simulate_sitting(rng, THETA, p, v)


def test_prior_draws_have_the_documented_shape_and_domains(rng):
    theta = sample_prior(rng, 1000, **PRIOR)
    A, B, sigma_eta, sigma_epsilon = theta.T
    assert theta.shape == (1000, 4)
    assert np.all((A > 0) & (A < 1) & (B > 0) & (B < 1))
    assert np.all((sigma_eta > 0) & (sigma_epsilon > 0))


def test_prior_draws_can_be_simulated(rng):
    p, v = sample_schedule(rng, **SCHEDULE)
    for theta in sample_prior(rng, 5, **PRIOR):
        assert np.all(np.isfinite(simulate_sitting(rng, theta, p, v)))


def test_schedules_start_with_baseline_and_use_only_the_four_kinds(rng):
    kinds = set(zip(BLOCK_P, BLOCK_V))
    for _ in range(200):
        p, v = sample_schedule(rng, **SCHEDULE)
        assert p.shape == v.shape and p.ndim == 1
        assert (p[0], v[0]) == (0.0, 1)
        assert set(zip(p, v)) <= kinds


def test_schedule_length_is_the_sum_of_its_blocks_within_the_block_counts(rng):
    # With every block exactly 20 trials long, T / 20 is the number of blocks.
    fixed_len = {**SCHEDULE, "mu_log_block_len": np.log(20), "sigma_log_block_len": 0}
    n_blocks = [len(sample_schedule(rng, **fixed_len)[0]) // 20 for _ in range(300)]
    assert min(n_blocks) >= SCHEDULE["n_blocks_min"]
    assert max(n_blocks) <= SCHEDULE["n_blocks_max"]


def test_schedule_rejects_an_impossible_block_range(rng):
    with pytest.raises(ValueError, match="n_blocks_min"):
        sample_schedule(rng, **{**SCHEDULE, "n_blocks_min": 0})
    with pytest.raises(ValueError, match="n_blocks_min"):
        sample_schedule(rng, **{**SCHEDULE, "n_blocks_min": 61})
