"""Code tests for src/designs/: the visuomotor adaptation Task and its Schedule Generator.

What the generated Schedules look like is in notebooks/working/one_state_priors.ipynb;
these are fast checks that the code does what its docstrings say.
"""

import numpy as np
import pytest

from designs import visuomotor_adaptation_experiment as des
from designs import visuomotor_adaptation_task as tsk

root_seed = 214923716987878841361447848104998594987  # secrets.randbits(128)

schedule_design = {
    "n_blocks_min": 5,
    "n_blocks_max": 16,
    "mu_log_block_len": 3.9,
    "sigma_log_block_len": 0.8,
    "trial_type_concentration": 3.0,
}


@pytest.fixture
def rng():
    return np.random.default_rng(root_seed)


def test_the_task_declares_its_conditions_and_observations():
    assert tsk.CONDITION_VARS == ("p", "v")
    assert tsk.OBSERVATION_VARS == ("y",)
    assert all(set(c) == set(tsk.CONDITION_VARS) for c in des.TRIAL_TYPES.values())


def test_schedules_start_with_baseline_and_use_only_the_trial_types(rng):
    trial_types = {(c["p"], c["v"]) for c in des.TRIAL_TYPES.values()}
    baseline = (des.TRIAL_TYPES["baseline"]["p"], des.TRIAL_TYPES["baseline"]["v"])
    for _ in range(200):
        schedule = des.sample_schedule(rng, schedule_design)
        assert set(schedule) == set(tsk.CONDITION_VARS)
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
    n_blocks = [len(des.sample_schedule(rng, fixed)["p"]) // 20 for _ in range(300)]
    assert min(n_blocks) >= schedule_design["n_blocks_min"]
    assert max(n_blocks) <= schedule_design["n_blocks_max"]


def test_schedule_design_errors_are_rejected(rng):
    with pytest.raises(ValueError, match="n_blocks_min"):
        des.sample_schedule(rng, {**schedule_design, "n_blocks_min": 0})
    with pytest.raises(ValueError, match="n_blocks_min"):
        des.sample_schedule(rng, {**schedule_design, "n_blocks_min": 17})
    with pytest.raises(ValueError, match="exactly the keys"):
        des.sample_schedule(rng, {**schedule_design, "kind_concentration": 3.0})
