"""Code tests for simulators/one_state.py: Simulator, Prior Sampler, Schedule Generator.

The scientific checks are in notebooks/working/one_state_simulator.ipynb (the Simulator)
and notebooks/working/one_state_priors.ipynb (Prior and Schedule Design); these are fast
checks that the functions do what their docstrings say.
"""

import numpy as np
import pytest

from simulators.one_state import (
    CONDITION_NAMES,
    PARAMETER_NAMES,
    TRIAL_TYPES,
    sample_prior,
    sample_schedule,
    simulate_sitting,
)

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


@pytest.fixture
def rng():
    return np.random.default_rng(root_seed)


def test_the_contract_names_match_the_model():
    assert PARAMETER_NAMES == ("A", "B", "sigma_eta", "sigma_epsilon")
    assert CONDITION_NAMES == ("p", "v")
    assert all(set(c) == set(CONDITION_NAMES) for c in TRIAL_TYPES.values())


def test_one_sitting_and_many_sittings_have_the_documented_shapes(rng):
    schedule = schedule_of(np.zeros(30), np.ones(30))
    assert simulate_sitting(rng, theta, schedule).shape == (30,)
    assert simulate_sitting(rng, theta, schedule, size=(7,)).shape == (7, 30)
    assert simulate_sitting(rng, theta, schedule, size=(2, 3)).shape == (2, 3, 30)


def test_the_same_generator_state_gives_the_same_sitting():
    schedule = schedule_of(np.repeat([0.0, 1.0, -1.0], 10), np.ones(30))
    y1 = simulate_sitting(np.random.default_rng(root_seed), theta, schedule)
    y2 = simulate_sitting(np.random.default_rng(root_seed), theta, schedule)
    np.testing.assert_array_equal(y1, y2)


def test_without_noise_a_learner_moves_to_the_fixed_point_geometrically(rng):
    # With vision and a constant p, y[t+1] - y* = (A - B) (y[t] - y*),
    # where y* = -B p / (1 - A + B).
    A, B = 0.95, 0.2
    y = simulate_sitting(rng, [A, B, tiny, tiny], schedule_of(np.ones(40), np.ones(40)))
    y_star = -B / (1 - A + B)
    expected = y_star + (0.0 - y_star) * (A - B) ** np.arange(40)
    np.testing.assert_allclose(y, expected, atol=1e-9)


def test_without_vision_the_plan_only_decays(rng):
    # Adapt for 30 trials with vision, then 20 trials without: y[t+1] = A y[t].
    A, B = 0.95, 0.2
    schedule = schedule_of(np.ones(50), np.r_[np.ones(30), np.zeros(20)])
    y = simulate_sitting(rng, [A, B, tiny, tiny], schedule)
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
        simulate_sitting(rng, bad_theta, schedule_of(np.zeros(5), np.ones(5)))


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
        simulate_sitting(rng, theta, schedule)


def test_prior_draws_have_the_documented_shape_and_domains(rng):
    draws = sample_prior(rng, 1000, prior)
    A, B, sigma_eta, sigma_epsilon = draws.T
    assert draws.shape == (1000, len(PARAMETER_NAMES))
    assert np.all((A > 0) & (A < 1) & (B > 0) & (B < 1))
    assert np.all((sigma_eta > 0) & (sigma_epsilon > 0))


def test_a_prior_with_missing_or_extra_constants_is_rejected(rng):
    with pytest.raises(ValueError, match="exactly the keys"):
        sample_prior(rng, 10, {k: v for k, v in prior.items() if k != "mu_logit_A"})
    with pytest.raises(ValueError, match="exactly the keys"):
        sample_prior(rng, 10, {**prior, "mu_logit_C": 0.0})


def test_prior_draws_can_be_simulated(rng):
    schedule = sample_schedule(rng, schedule_design)
    for draw in sample_prior(rng, 5, prior):
        assert np.all(np.isfinite(simulate_sitting(rng, draw, schedule)))


def test_schedules_start_with_baseline_and_use_only_the_trial_types(rng):
    trial_types = {(c["p"], c["v"]) for c in TRIAL_TYPES.values()}
    baseline = (TRIAL_TYPES["baseline"]["p"], TRIAL_TYPES["baseline"]["v"])
    for _ in range(200):
        schedule = sample_schedule(rng, schedule_design)
        assert set(schedule) == set(CONDITION_NAMES)
        p, v = schedule["p"], schedule["v"]
        assert p.shape == v.shape and p.ndim == 1
        assert (p[0], v[0]) == baseline
        assert set(zip(p, v)) <= trial_types


def test_schedule_length_is_the_sum_of_its_blocks_within_the_block_counts(rng):
    # With every Block exactly 20 Trials long, T / 20 is the number of Blocks.
    fixed = {
        **schedule_design,
        "mu_log_block_len": np.log(20),
        "sigma_log_block_len": 0,
    }
    n_blocks = [len(sample_schedule(rng, fixed)["p"]) // 20 for _ in range(300)]
    assert min(n_blocks) >= schedule_design["n_blocks_min"]
    assert max(n_blocks) <= schedule_design["n_blocks_max"]


def test_schedule_design_errors_are_rejected(rng):
    with pytest.raises(ValueError, match="n_blocks_min"):
        sample_schedule(rng, {**schedule_design, "n_blocks_min": 0})
    with pytest.raises(ValueError, match="n_blocks_min"):
        sample_schedule(rng, {**schedule_design, "n_blocks_min": 17})
    with pytest.raises(ValueError, match="exactly the keys"):
        sample_schedule(rng, {**schedule_design, "kind_concentration": 3.0})
