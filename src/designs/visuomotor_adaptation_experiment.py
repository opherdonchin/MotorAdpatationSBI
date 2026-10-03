"""Experiment designs for the visuomotor adaptation Task.

Everything needed to create Experiments of this Task: the Trial Types and the Schedule
Designs, with their Schedule Generators. For now one Schedule Design: random Blocks of
the four Trial Types (decision 0005), drawn by `sample_schedule`. Terms:
docs/glossary.md; where this module fits: decision 0006.
"""

import types

import numpy as np

from designs import visuomotor_adaptation_task as tsk

# The Trial Types, with the value of each Condition in CONDITION_VARS.
TRIAL_TYPES = types.MappingProxyType(
    {
        "baseline": {"p": 0.0, "v": 1},
        "+1": {"p": 1.0, "v": 1},
        "-1": {"p": -1.0, "v": 1},
        "no vision": {"p": 0.0, "v": 0},
    }
)


def sample_schedule(rng, schedule_design):
    """Schedule Generator: draw the Schedule of one Sitting.

    A Schedule is the Condition on every Trial, here the perturbation and the vision
    flag. Following the Schedule Design of decision 0005, every Block is a run of Trials
    of one Trial Type (`TRIAL_TYPES`): the number of Blocks is uniform on
    n_blocks_min..n_blocks_max; Block lengths are independent and log-normal, rounded
    to whole Trials; the Sitting's proportions of the Trial Types are drawn from a
    symmetric Dirichlet with the given concentration; the first Block is a baseline and
    every later Block's Trial Type is drawn independently with those proportions. Two
    neighbouring Blocks of the same Trial Type are, in effect, one longer Block. The
    Blocks themselves are not returned: they are part of the Schedule Design, not of
    the Schedule.

    Parameters
    ----------
    rng : numpy.random.Generator
        Source of the draws. It is advanced (the only side effect).
    schedule_design : dict
        The Schedule Design's constants, exactly these keys: ``n_blocks_min`` and
        ``n_blocks_max`` (int; smallest and largest number of Blocks, both included,
        1 <= min <= max); ``mu_log_block_len`` and ``sigma_log_block_len`` (float; mean
        and standard deviation of the log of a Block's length in Trials);
        ``trial_type_concentration`` (float; concentration of the symmetric Dirichlet
        over the Trial Types, for each Trial Type; larger values make the proportions
        more alike).

    Returns
    -------
    schedule : dict
        The Schedule, keyed by `CONDITION_VARS` of the Task: ``"p"``, the perturbation on each
        Trial (float, shape (T,): 0, +1 or -1, and 0 on no-vision Trials), and ``"v"``,
        the vision flag on each Trial (int, shape (T,): 1, or 0 in no-vision Blocks).

    Raises
    ------
    ValueError
        If `schedule_design` does not have exactly the keys listed above, or the Block
        counts do not satisfy 1 <= n_blocks_min <= n_blocks_max.
    """
    keys = {
        "n_blocks_min",
        "n_blocks_max",
        "mu_log_block_len",
        "sigma_log_block_len",
        "trial_type_concentration",
    }
    if set(schedule_design) != keys:
        raise ValueError(
            f"schedule_design must have exactly the keys {sorted(keys)}, "
            f"got {sorted(schedule_design)}"
        )
    n_min, n_max = schedule_design["n_blocks_min"], schedule_design["n_blocks_max"]
    if not 1 <= n_min <= n_max:
        raise ValueError(
            f"need 1 <= n_blocks_min <= n_blocks_max, got {n_min} and {n_max}"
        )
    n_blocks = rng.integers(n_min, n_max + 1)
    log_len = rng.normal(
        schedule_design["mu_log_block_len"],
        schedule_design["sigma_log_block_len"],
        n_blocks,
    )
    block_len = np.rint(np.exp(log_len)).astype(int)
    n_types = len(TRIAL_TYPES)
    concentration = np.full(n_types, schedule_design["trial_type_concentration"])
    proportions = rng.dirichlet(concentration)
    later_types = rng.choice(n_types, size=n_blocks - 1, p=proportions)
    block_type = np.concatenate([[0], later_types])  # the first Block is a baseline
    # For each Condition, its value in each Trial Type, then on every Trial.
    by_type = {
        name: np.array([conditions[name] for conditions in TRIAL_TYPES.values()])
        for name in tsk.CONDITION_VARS
    }
    return {
        name: np.repeat(values[block_type], block_len)
        for name, values in by_type.items()
    }
