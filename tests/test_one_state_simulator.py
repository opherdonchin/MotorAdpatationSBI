"""Code tests for the one-state simulator (simulators/one_state.py).

The scientific checks (noise-free learning curves, steady-state statistics) are in
notebooks/one_state_simulator.ipynb; these are fast checks that the function does what
its docstring says.
"""

import numpy as np
import pytest

from simulators.one_state import simulate_sitting

ROOT_SEED = 68921609159653578200335664192142966917  # secrets.randbits(128)

THETA = np.array([0.95, 0.2, 0.05, 0.15])  # A, B, sigma_eta, sigma_epsilon
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
