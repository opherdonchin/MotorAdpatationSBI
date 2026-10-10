"""Code tests for src/motor_sbi/experiments.py: simulating, saving and loading Experiments."""

import types

import numpy as np
import pytest

from designs import visuomotor_adaptation_experiment as des
from models import one_state as mdl
from motor_sbi import experiments

root_seed = 231277218653041434355576336144248683381  # secrets.randbits(128)

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
    "n_blocks_min": 2,
    "n_blocks_max": 4,
    "mu_log_block_len": 2.5,
    "sigma_log_block_len": 0.3,
    "trial_type_concentration": 3.0,
}


def simulate(seed=root_seed, design=schedule_design, n=20):
    return experiments.simulate_experiment(
        np.random.default_rng(seed), mdl, prior, des.sample_schedule, design, n
    )


def test_sittings_hold_only_conditions_and_observations():
    sittings, ground_truth = simulate()
    names = {*mdl.TASK.CONDITION_VARS, *mdl.TASK.OBSERVATION_VARS}
    assert len(sittings) == len(ground_truth) == 20
    for sitting, truth in zip(sittings, ground_truth):
        assert set(sitting) == names
        assert len({len(values) for values in sitting.values()}) == 1
        assert set(truth) == {*mdl.PARAMETERS, "x"}
        assert truth["x"].shape == sitting["y"].shape


def test_the_same_seed_gives_the_same_experiment():
    first, _ = simulate()
    second, _ = simulate()
    for a, b in zip(first, second):
        for name in a:
            np.testing.assert_array_equal(a[name], b[name])


def test_changing_the_schedule_design_leaves_the_parameter_draws_unchanged():
    _, truth_a = simulate()
    _, truth_b = simulate(design={**schedule_design, "n_blocks_max": 8})
    for a, b in zip(truth_a, truth_b):
        assert [a[name] for name in mdl.PARAMETERS] == [
            b[name] for name in mdl.PARAMETERS
        ]


def test_sittings_can_share_schedules_and_keep_their_own_parameters():
    rng = np.random.default_rng(root_seed)
    sittings, ground_truth = experiments.simulate_experiment(
        rng, mdl, prior, des.sample_schedule, schedule_design, 12, 4
    )
    assert len(sittings) == 12
    for first in range(0, 12, 4):
        for sitting in sittings[first + 1 : first + 4]:
            for name in mdl.TASK.CONDITION_VARS:
                np.testing.assert_array_equal(sitting[name], sittings[first][name])
    assert len({truth["A"] for truth in ground_truth}) == 12
    # the parameter draws are those of an Experiment with one Schedule per Sitting
    _, truth_own = simulate(n=12)
    assert [t["A"] for t in ground_truth] == [t["A"] for t in truth_own]


def test_sittings_per_schedule_must_divide_the_number_of_sittings():
    with pytest.raises(ValueError, match="n_sittings_per_schedule"):
        experiments.simulate_experiment(
            np.random.default_rng(root_seed),
            mdl,
            prior,
            des.sample_schedule,
            schedule_design,
            10,
            4,
        )


def test_any_module_with_the_right_names_can_be_simulated():
    # A stand-in Model: one parameter, one Condition, one Observation.
    task = types.SimpleNamespace(CONDITION_VARS=("c",), OBSERVATION_VARS=("o",))
    model = types.SimpleNamespace(
        TASK=task,
        PARAMETERS=("k",),
        sample_prior=lambda rng, size, prior: rng.normal(size=(size, 1)),
        simulate_sitting=lambda rng, theta, schedule: (
            {"o": theta[0] * schedule["c"]},
            {"k": float(theta[0])},
        ),
    )
    sittings, ground_truth = experiments.simulate_experiment(
        np.random.default_rng(root_seed),
        model,
        {},
        lambda rng, design: {"c": np.arange(design["n"], dtype=float)},
        {"n": 5},
        3,
    )
    for sitting, truth in zip(sittings, ground_truth):
        np.testing.assert_allclose(sitting["o"], truth["k"] * np.arange(5))


def test_saving_and_loading_gives_back_the_same_sittings_and_ground_truth(tmp_path):
    sittings, ground_truth = simulate()
    record = {"model": "one_state", "n_sittings": 20}
    experiments.save_experiment(tmp_path, sittings, ground_truth, record)
    loaded = experiments.load_sittings(tmp_path)
    assert len(loaded) == len(sittings)
    for a, b in zip(sittings, loaded):
        assert set(a) == set(b)
        for name in a:
            np.testing.assert_array_equal(a[name], b[name])
    truth, loaded_record = experiments.load_ground_truth(tmp_path)
    assert loaded_record == record
    np.testing.assert_array_equal(truth["A"], [t["A"] for t in ground_truth])
    np.testing.assert_array_equal(
        truth["x"], np.concatenate([t["x"] for t in ground_truth])
    )


def test_an_actual_experiment_is_saved_without_ground_truth(tmp_path):
    sittings, _ = simulate(n=3)
    experiments.save_experiment(tmp_path, sittings)
    assert sorted(p.name for p in tmp_path.iterdir()) == ["sittings.npz"]
    with pytest.raises(FileNotFoundError):
        experiments.load_ground_truth(tmp_path)
