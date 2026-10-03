# 0006 — Data classes for Sittings, Schedules and parameters; no Model class yet

**Date:** 2026-10-03 · **Status:** Proposed

**Context:** The one-state Runnables pass loosely related arrays. A Schedule is two
arrays (`p`, `v`) passed side by side; parameter values are a 4-column array whose
meaning depends on a column order; the Prior Sampler takes eight keyword arguments; and
step C3 of [#12](https://github.com/opherdonchin/MotorAdpatationSBI/issues/12) will add
the Ground Truth, which must travel with a Simulated Sitting but stay apart from it.
Opher [asked](https://github.com/opherdonchin/MotorAdpatationSBI/pull/18#issuecomment-5968856811)
whether Models should be classes, possibly with separate classes for Models and Sittings.
`AGENTS.md` asks for classes to be discussed first.

**Decision** (terms as in the [glossary](../glossary.md)):

1. **Data are frozen dataclasses** (Python's standard `dataclasses`, `frozen=True`), each
   holding arrays: a *struct of arrays*. A batch of many Sittings is one object whose
   fields have a leading batch dimension, so code stays vectorized.
2. **Task-level classes,** shared by every Model of the Task, in `src/motor_sbi/`:
   - `Schedule`: the Conditions, `p` and `v`, each of shape `(..., T)`.
   - `Sitting`: a `Schedule` and the movements `y`, of shape `(..., T)`.
3. **Model-level classes,** in the Model's module in `simulators/` (for the one-state
   Model, `simulators/one_state.py`):
   - `Parameters`: one field per parameter (`A`, `B`, `sigma_eta`, `sigma_epsilon`),
     each an array with the batch shape. Conversion to and from a flat vector, for
     BayesFlow and PyMC, is defined once, in this class; it replaces the "parameter
     order" convention.
   - `GroundTruth`: the `Parameters` and the hidden plans `x`, of shape `(..., T)`.
   - `Prior`: the constants of the Prior (the eight `mu_*` and `sigma_*`), with a
     constructor from the stated 95% ranges.
   - `ScheduleDesign`: the constants of the Schedule Design (Block counts and lengths,
     Dirichlet concentration).
4. **Runnables stay functions** in the Model's module, taking and returning these
   classes: the Prior Sampler maps a `Prior` to `Parameters`, the Schedule Generator maps
   a `ScheduleDesign` to a `Schedule`, and the Simulator maps `Parameters` and a
   `Schedule` to a `Sitting` and its `GroundTruth`.
5. **Input checks move into the classes:** each checks its own fields once, when it is
   created (shapes agree, `v` is 0 or 1, parameters are in their domains). That is the
   public boundary of `AGENTS.md`'s input-checking rule; functions receiving these
   classes trust them.
6. **No Model class yet.** A Model is its module, with the standard names above. A Model
   class (or a shared interface every Model module follows) is decided when a second
   Model, or the first code that works with "any Model", needs it.

**Why:** Named fields replace positional conventions (the column order of `theta`, `p`
and `v` passed as a pair), so a mistake is an error rather than a silent swap.
Separating `Sitting` from `GroundTruth` by type makes the blindness rule of `AGENTS.md`
something the code shows: an Analysis is given Sittings, and only a Check is given
Ground Truth. Struct-of-arrays keeps array operations vectorized; frozen classes cannot
be changed after they are checked. `dataclasses` is in the standard library, so there is
no new dependency.

*Alternatives:* plain dicts of arrays (BayesFlow's native format, but no checked fields,
and typos in keys go unnoticed; a dataclass converts to one in a line when BayesFlow
needs it); named tuples (immutable, but positional, the problem being removed);
`xarray` datasets (labelled dimensions, good for variable lengths and storage, heavier
than needed now; worth reconsidering when storage formats are aligned); a validation
library such as `pydantic` (more checking machinery than this needs); a Model class now
(one Model, and no code yet that works with any Model).

**Consequences:**

- The signatures of `simulate_sitting`, `sample_prior` and `sample_schedule` change, and
  so do their tests and the two working notebooks. I propose doing that as its own small
  PR before step C3, with no change in behaviour (same seeds, same numbers).
- Sittings of different lengths cannot share one batch object. Until storage formats
  are aligned, a collection of them is a list of `Sitting`; padding, or `xarray`, can
  replace that later.
- What generic code (BayesFlow training, SBC) needs from a Model will become visible in
  steps C3 and stage 2, which is the evidence point 6 waits for.
