"""Code tests for src/models/one_state.py: the Simulator and the Prior Sampler.

The scientific checks are in notebooks/working/one_state_simulator.ipynb (the Simulator)
and notebooks/working/one_state_priors.ipynb (the Prior); these are fast checks that the
functions do what their docstrings say.
"""

import numpy as np
import pytest

from designs import visuomotor_adaptation_experiment as des
from models import one_state as mdl

root_seed = 68921609159653578200335664192142966917  # secrets.randbits(128)

theta = np.array([0.95, 0.2, 0.05, 0.15])  # A, B, sigma_eta, sigma_epsilon
prior = {
    "mu_logit_A": 4.0,
    "sigma_logit_A": 1.5,
    "mu_logit_B": -2.3,
    "sigma_logit_B": 1.2,
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
    assert mdl.PARAMETERS == ("A", "B", "sigma_eta", "sigma_epsilon")
    assert mdl.TASK.CONDITION_VARS == ("p", "v")


def test_the_simulator_returns_observations_and_ground_truth(rng):
    schedule = schedule_of(np.zeros(30), np.ones(30))
    observations, ground_truth = mdl.simulate_sitting(rng, theta, schedule, size=(4,))
    assert set(observations) == set(mdl.TASK.OBSERVATION_VARS)
    assert observations["y"].shape == (4, 30)
    assert set(ground_truth) == {*mdl.PARAMETERS, "x"}
    assert ground_truth["x"].shape == (4, 30)
    assert [ground_truth[name] for name in mdl.PARAMETERS] == theta.tolist()


def test_with_negligible_execution_noise_the_movement_is_the_plan(rng):
    schedule = schedule_of(np.ones(30), np.ones(30))
    observations, ground_truth = mdl.simulate_sitting(
        rng, [0.95, 0.2, 0.05, tiny], schedule
    )
    np.testing.assert_allclose(observations["y"], ground_truth["x"], atol=1e-9)


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


def test_without_noise_a_learner_moves_to_the_fixed_point_geometrically(rng):
    # With vision and a constant p, y[t+1] - y* = (A - B) (y[t] - y*),
    # where y* = -B p / (1 - A + B).
    A, B = 0.95, 0.2
    y = movements(rng, [A, B, tiny, tiny], schedule_of(np.ones(40), np.ones(40)))
    y_star = -B / (1 - A + B)
    expected = y_star + (0.0 - y_star) * (A - B) ** np.arange(40)
    np.testing.assert_allclose(y, expected, atol=1e-9)


def test_without_vision_the_plan_only_decays(rng):
    # Adapt for 30 trials with vision, then 20 trials without: y[t+1] = A y[t].
    A, B = 0.95, 0.2
    schedule = schedule_of(np.ones(50), np.r_[np.ones(30), np.zeros(20)])
    y = movements(rng, [A, B, tiny, tiny], schedule)
    np.testing.assert_allclose(y[31:], A * y[30:-1], atol=1e-9)


@pytest.mark.parametrize(
    "bad_theta, message",
    [
        ([0.95, 0.2, 0.05], "shape"),
        ([1.0, 0.2, 0.05, 0.15], "between 0 and 1"),
        ([0.95, 0.0, 0.05, 0.15], "between 0 and 1"),
        ([0.95, 0.2, 0.0, 0.15], "positive"),
        ([0.95, 0.2, 0.05, -0.1], "positive"),
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


def test_prior_draws_have_the_documented_shape_and_domains(rng):
    draws = mdl.sample_prior(rng, 1000, prior)
    A, B, sigma_eta, sigma_epsilon = draws.T
    assert draws.shape == (1000, len(mdl.PARAMETERS))
    assert np.all((A > 0) & (A < 1) & (B > 0) & (B < 1))
    assert np.all((sigma_eta > 0) & (sigma_epsilon > 0))


def test_a_prior_with_missing_or_extra_constants_is_rejected(rng):
    with pytest.raises(ValueError, match="exactly the keys"):
        mdl.sample_prior(rng, 10, {k: v for k, v in prior.items() if k != "mu_logit_A"})
    with pytest.raises(ValueError, match="exactly the keys"):
        mdl.sample_prior(rng, 10, {**prior, "mu_logit_C": 0.0})


def test_prior_draws_can_be_simulated(rng):
    schedule = des.sample_schedule(rng, schedule_design)
    for draw in mdl.sample_prior(rng, 5, prior):
        assert np.all(np.isfinite(movements(rng, draw, schedule)))
