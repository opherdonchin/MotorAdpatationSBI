"""Code tests for src/models/two_state.py: the Simulator and the Prior Sampler.

The scientific checks are in notebooks/working/two_state_simulator.ipynb; these are fast
checks that the functions do what their docstrings say.
"""

import numpy as np
import pytest

from designs import visuomotor_adaptation_experiment as des
from models import one_state
from models import two_state as mdl

root_seed = 147714581166052409098528462437566379683  # secrets.randbits(128)

# A_fast, A_slow, B_fast, B_slow, sigma_eta, sigma_epsilon
theta = np.array([0.6, 0.99, 0.2, 0.02, 0.02, 0.15])
prior = {
    "mu_logit_A_fast": 1.05,
    "sigma_logit_A_fast": 0.97,
    "mu_log_A_diff": 1.18,
    "sigma_log_A_diff": 0.39,
    "mu_logit_B_fast": -1.27,
    "sigma_logit_B_fast": 0.85,
    "mu_log_B_diff": 0.63,
    "sigma_log_B_diff": 0.5,
    "mu_log_sigma_epsilon": -1.9,
    "sigma_log_sigma_epsilon": 0.4,
    "mu_log_ratio": -2.2,
    "sigma_log_ratio": 0.3,
}
schedule_design = {
    "n_blocks_min": 5,
    "n_blocks_max": 16,
    "mu_log_block_len": 3.9,
    "sigma_log_block_len": 0.8,
    "trial_type_concentration": 3.0,
}
tiny = 1e-12  # noise standard deviation small enough to make a Sitting deterministic


def schedule_of(p, v):
    return {"p": np.asarray(p, dtype=float), "v": np.asarray(v)}


def movements(rng, theta, schedule, size=()):
    observations, _ = mdl.simulate_sitting(rng, theta, schedule, size)
    return observations["y"]


@pytest.fixture
def rng():
    return np.random.default_rng(root_seed)


def test_the_model_names_its_task_and_parameters():
    assert mdl.PARAMETERS == (
        "A_fast",
        "A_slow",
        "B_fast",
        "B_slow",
        "sigma_eta",
        "sigma_epsilon",
    )
    assert mdl.TASK.CONDITION_VARS == ("p", "v")


def test_the_simulator_returns_observations_and_ground_truth(rng):
    schedule = schedule_of(np.zeros(30), np.ones(30))
    observations, ground_truth = mdl.simulate_sitting(rng, theta, schedule, size=(4,))
    assert set(observations) == set(mdl.TASK.OBSERVATION_VARS)
    assert observations["y"].shape == (4, 30)
    assert set(ground_truth) == {*mdl.PARAMETERS, "x_fast", "x_slow"}
    assert ground_truth["x_fast"].shape == (4, 30)
    assert ground_truth["x_slow"].shape == (4, 30)
    assert [ground_truth[name] for name in mdl.PARAMETERS] == theta.tolist()


def test_with_negligible_execution_noise_the_movement_is_the_sum_of_the_states(rng):
    schedule = schedule_of(np.ones(30), np.ones(30))
    observations, ground_truth = mdl.simulate_sitting(
        rng, [0.6, 0.99, 0.2, 0.02, 0.05, tiny], schedule
    )
    np.testing.assert_allclose(
        observations["y"], ground_truth["x_fast"] + ground_truth["x_slow"], atol=1e-9
    )


def test_one_sitting_and_many_sittings_have_the_documented_shapes(rng):
    schedule = schedule_of(np.zeros(30), np.ones(30))
    assert movements(rng, theta, schedule).shape == (30,)
    assert movements(rng, theta, schedule, size=(7,)).shape == (7, 30)
    assert movements(rng, theta, schedule, size=(2, 3)).shape == (2, 3, 30)


def test_the_same_generator_state_gives_the_same_sitting():
    schedule = schedule_of(np.repeat([0.0, 1.0, -1.0], 10), np.ones(30))
    y1 = movements(np.random.default_rng(root_seed), theta, schedule)
    y2 = movements(np.random.default_rng(root_seed), theta, schedule)
    np.testing.assert_array_equal(y1, y2)


def test_without_noise_the_states_follow_the_matrix_solution(rng):
    # With vision and a constant p the two states obey s[t+1] = S s[t] - b p, with
    # S = diag(A) - b 1', so s[t] = s* + S^t (s[0] - s*) and s* = -(I - S)^-1 b p.
    A_fast, A_slow, B_fast, B_slow = theta[:4]
    b = np.array([B_fast, B_slow])
    step = np.diag([A_fast, A_slow]) - np.outer(b, np.ones(2))
    s_star = -np.linalg.solve(np.eye(2) - step, b)
    expected = np.array(
        [s_star - np.linalg.matrix_power(step, t) @ s_star for t in range(40)]
    )
    _, ground_truth = mdl.simulate_sitting(
        rng, [*theta[:4], tiny, tiny], schedule_of(np.ones(40), np.ones(40))
    )
    np.testing.assert_allclose(ground_truth["x_fast"], expected[:, 0], atol=1e-9)
    np.testing.assert_allclose(ground_truth["x_slow"], expected[:, 1], atol=1e-9)


def test_without_vision_each_state_decays_by_its_own_retention(rng):
    # Adapt for 30 trials with vision, then 20 trials without.
    A_fast, A_slow = theta[:2]
    schedule = schedule_of(np.ones(50), np.r_[np.ones(30), np.zeros(20)])
    _, ground_truth = mdl.simulate_sitting(rng, [*theta[:4], tiny, tiny], schedule)
    x_fast, x_slow = ground_truth["x_fast"], ground_truth["x_slow"]
    np.testing.assert_allclose(x_fast[31:], A_fast * x_fast[30:-1], atol=1e-9)
    np.testing.assert_allclose(x_slow[31:], A_slow * x_slow[30:-1], atol=1e-9)


def test_with_equal_retentions_the_movement_is_that_of_the_one_state_model(rng):
    # At the edge of the domain, A_fast = A_slow = A, the plan x_fast + x_slow follows
    # the one-state Model with B = B_fast + B_slow. Checked here without noise.
    A, B_fast, B_slow = 0.95, 0.15, 0.05
    schedule = schedule_of(
        np.repeat([0.0, 1.0, 0.0, -1.0], 20),
        np.r_[np.ones(40), np.zeros(20), np.ones(20)],
    )
    y_two = movements(
        rng, [A, np.nextafter(A, 1), B_fast, B_slow, tiny, tiny], schedule
    )
    y_one = one_state.simulate_sitting(rng, [A, B_fast + B_slow, tiny, tiny], schedule)[
        0
    ]["y"]
    np.testing.assert_allclose(y_two, y_one, atol=1e-9)


def test_after_a_short_reversal_the_movement_recovers_spontaneously(rng):
    # Adaptation to +1 moves y toward -1. A short reversal brings y back to about zero
    # by pushing the fast state the other way; without vision the fast state then
    # decays and the slow state's adaptation reappears (Smith et al. 2006).
    schedule = schedule_of(
        np.r_[np.ones(200), -np.ones(12), np.zeros(40)],
        np.r_[np.ones(212), np.zeros(40)],
    )
    y = movements(rng, [0.6, 0.99, 0.2, 0.02, tiny, tiny], schedule)
    no_vision = y[212:]
    assert no_vision.min() < no_vision[0] - 0.1


@pytest.mark.parametrize(
    "bad_theta, message",
    [
        ([0.6, 0.99, 0.2, 0.02, 0.02], "shape"),
        ([0.6, 1.0, 0.2, 0.02, 0.02, 0.15], "between 0 and 1"),
        ([0.6, 0.99, 0.2, 0.0, 0.02, 0.15], "between 0 and 1"),
        ([0.99, 0.6, 0.2, 0.02, 0.02, 0.15], "ordered"),
        ([0.6, 0.99, 0.02, 0.2, 0.02, 0.15], "ordered"),
        ([0.6, 0.99, 0.2, 0.02, 0.0, 0.15], "positive"),
        ([0.6, 0.99, 0.2, 0.02, 0.02, -0.1], "positive"),
    ],
)
def test_parameters_outside_their_domain_are_rejected(rng, bad_theta, message):
    with pytest.raises(ValueError, match=message):
        mdl.simulate_sitting(rng, bad_theta, schedule_of(np.zeros(5), np.ones(5)))


@pytest.mark.parametrize(
    "schedule, message",
    [
        ({"p": np.zeros(5)}, "exactly the keys"),
        ({"p": np.zeros(5), "v": np.ones(5), "cue": np.ones(5)}, "exactly the keys"),
        (schedule_of(np.zeros((2, 5)), np.ones(5)), "one-dimensional"),
        (schedule_of(np.zeros(5), np.ones((2, 5))), "one-dimensional"),
        (schedule_of(np.zeros(5), np.ones(4)), "same length"),
        (schedule_of(np.zeros(5), np.full(5, 0.5)), "only 0 and 1"),
    ],
)
def test_malformed_schedules_are_rejected(rng, schedule, message):
    with pytest.raises(ValueError, match=message):
        mdl.simulate_sitting(rng, theta, schedule)


def test_prior_draws_have_the_documented_shape_domains_and_ordering(rng):
    draws = mdl.sample_prior(rng, 1000, prior)
    A_fast, A_slow, B_fast, B_slow, sigma_eta, sigma_epsilon = draws.T
    assert draws.shape == (1000, len(mdl.PARAMETERS))
    assert np.all((draws[:, :4] > 0) & (draws[:, :4] < 1))
    assert np.all((A_fast < A_slow) & (B_fast > B_slow))
    assert np.all((sigma_eta > 0) & (sigma_epsilon > 0))


def test_unstable_prior_draws_are_drawn_again(rng):
    # A Prior whose adaptation rates are nearly all close to 1 puts most draws outside
    # the stable region; every draw returned must still be inside it.
    eager = {**prior, "mu_logit_B_fast": 6.0, "mu_log_B_diff": -2.0}
    A_fast, A_slow, B_fast, B_slow, _, _ = mdl.sample_prior(rng, 500, eager).T
    assert np.all(B_fast / (1 + A_fast) + B_slow / (1 + A_slow) < 1)


def test_a_prior_with_missing_or_extra_constants_is_rejected(rng):
    with pytest.raises(ValueError, match="exactly the keys"):
        mdl.sample_prior(
            rng, 10, {k: v for k, v in prior.items() if k != "mu_log_A_diff"}
        )
    with pytest.raises(ValueError, match="exactly the keys"):
        mdl.sample_prior(rng, 10, {**prior, "mu_logit_C": 0.0})


def test_prior_draws_can_be_simulated(rng):
    schedule = des.sample_schedule(rng, schedule_design)
    for draw in mdl.sample_prior(rng, 5, prior):
        assert np.all(np.isfinite(movements(rng, draw, schedule)))
