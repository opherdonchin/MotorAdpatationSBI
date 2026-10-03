"""Simulated Experiments, for any Model: simulating them, saving them, loading them.

Uses only the names every Model module and Task module provide (decision 0006): a Model's
`TASK`, `PARAMETERS`, `sample_prior` and `simulate_sitting`, and its Task's
`CONDITION_VARS` and `OBSERVATION_VARS`. Terms: docs/glossary.md.

On disk, an Experiment is a folder. `sittings.npz` holds one row per Trial: the
Sitting it belongs to, the Trial's number within the Sitting, and one column per
Condition and Observation. A Simulated Experiment also has `ground_truth.npz` (the
parameter values of each Sitting, and the hidden states per Trial, in the same row order)
and `record.json` (what produced it). Analyses read only `sittings.npz`.
"""

import json
import pathlib

import numpy as np


def simulate_experiment(
    rng, model, prior, schedule_generator, schedule_design, n_sittings
):
    """Simulate an Experiment: one Schedule and one parameter draw per Sitting.

    For each of `n_sittings` Sittings: draw parameter values with the Model's Prior
    Sampler, draw a Schedule with the Schedule Generator, and simulate the movements
    with the Model's Simulator. Three streams spawned from `rng` serve the three
    purposes, so changing one (for example the Schedule Design) leaves the draws of
    the others unchanged.

    Parameters
    ----------
    rng : numpy.random.Generator
        Root of the three streams. It is advanced by the spawn (the only side effect).
    model : module
        A Model module: provides `TASK`, `PARAMETERS`, `sample_prior` and
        `simulate_sitting`.
    prior : dict
        The Prior's constants, passed to `model.sample_prior`.
    schedule_generator : callable
        A Schedule Generator for the Model's Task, called as
        ``schedule_generator(rng, schedule_design)`` and returning a Schedule: a dict
        with one array of shape (T,) per name in ``model.TASK.CONDITION_VARS``.
    schedule_design : dict
        The Schedule Design's constants, passed to `schedule_generator`.
    n_sittings : int
        Number of Sittings, each with its own parameter values and Schedule.

    Returns
    -------
    sittings : list of dict
        One dict per Sitting: the Schedule's arrays and the Observations' arrays, each
        of shape (T,), keyed by ``CONDITION_VARS`` and ``OBSERVATION_VARS``. Nothing
        else: no parameter values.
    ground_truth : list of dict
        One dict per Sitting, in the same order, as returned by the Simulator: the
        parameter values (one float per name in ``model.PARAMETERS``) and the hidden
        states, arrays of shape (T,).
    """
    rng_prior, rng_schedule, rng_sim = rng.spawn(3)
    theta = model.sample_prior(rng_prior, n_sittings, prior)
    sittings, ground_truth = [], []
    for theta_i in theta:
        schedule = schedule_generator(rng_schedule, schedule_design)
        observations, truth = model.simulate_sitting(rng_sim, theta_i, schedule)
        sittings.append({**schedule, **observations})
        ground_truth.append(truth)
    return sittings, ground_truth


def save_experiment(folder, sittings, ground_truth=None, record=None):
    """Save an Experiment to a folder: its Sittings, and for a Simulated one, the rest.

    Parameters
    ----------
    folder : str or pathlib.Path
        Folder to write to; created if missing. Files already there are overwritten.
    sittings : list of dict
        As returned by `simulate_experiment`: per-Trial arrays of equal length within a
        Sitting, with the same keys in every Sitting.
    ground_truth : list of dict, optional
        As returned by `simulate_experiment`. Scalars are saved one per Sitting, arrays
        one per Trial. Omitted for an Actual Experiment.
    record : dict, optional
        What produced the Experiment (for example the Model, the Prior, the Schedule
        Design, the root seed and the git commit). Must be serializable as JSON.

    Returns
    -------
    folder : pathlib.Path
        The folder written to.
    """
    folder = pathlib.Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    lengths = [len(next(iter(sitting.values()))) for sitting in sittings]
    index = {
        "sitting": np.repeat(np.arange(len(sittings)), lengths),
        "trial": np.concatenate([np.arange(n) for n in lengths]),
    }
    np.savez_compressed(folder / "sittings.npz", **index, **_stack(sittings))
    if ground_truth is not None:
        np.savez_compressed(folder / "ground_truth.npz", **_stack(ground_truth))
    if record is not None:
        (folder / "record.json").write_text(json.dumps(record, indent=2))
    return folder


def load_sittings(folder):
    """Load the Sittings of an Experiment saved by `save_experiment`.

    Parameters
    ----------
    folder : str or pathlib.Path
        The Experiment's folder.

    Returns
    -------
    sittings : list of dict
        One dict per Sitting, in the saved order, with one array of shape (T,) per
        saved Condition and Observation.
    """
    columns = dict(np.load(pathlib.Path(folder) / "sittings.npz"))
    sitting = columns.pop("sitting")
    columns.pop("trial")
    starts = np.flatnonzero(np.diff(sitting, prepend=-1))
    return [
        {name: values[start:stop] for name, values in columns.items()}
        for start, stop in zip(starts, np.append(starts[1:], len(sitting)))
    ]


def load_ground_truth(folder):
    """Load the Ground Truth and record of a Simulated Experiment.

    Parameters
    ----------
    folder : str or pathlib.Path
        The Experiment's folder.

    Returns
    -------
    ground_truth : dict of numpy.ndarray
        Parameter values, one entry per Sitting, and hidden states, one entry per Trial
        in the row order of ``sittings.npz``.
    record : dict
        What produced the Experiment, as saved.
    """
    folder = pathlib.Path(folder)
    ground_truth = dict(np.load(folder / "ground_truth.npz"))
    record = json.loads((folder / "record.json").read_text())
    return ground_truth, record


def _stack(rows):
    """Turn a list of dicts with the same keys into one dict of arrays.

    Parameters
    ----------
    rows : list of dict
        Each dict maps the same names to scalars or to one-dimensional arrays.

    Returns
    -------
    stacked : dict of numpy.ndarray
        For a name whose values are scalars, an array with one entry per row; for a
        name whose values are arrays, their concatenation across rows.
    """
    return {
        name: (
            np.concatenate([row[name] for row in rows])
            if np.ndim(rows[0][name])
            else np.array([row[name] for row in rows])
        )
        for name in rows[0]
    }
