# 0006 — Models, Tasks and Experiment designs: separate modules, named contracts, no classes

**Date:** 2026-10-03 · **Status:** Proposed

**Context:** The one-state Runnables passed loosely related values: a Schedule as two
arrays side by side, parameter values as a 4-column array whose meaning depended on a
column order, and the Prior's constants as eight separate arguments. Opher
[asked](https://github.com/opherdonchin/MotorAdpatationSBI/pull/18#issuecomment-5968856811)
whether Models should be classes. A first draft of this record proposed data classes;
Opher rejected that as too much structure for a project looking for an easy win, and
[asked](https://github.com/opherdonchin/MotorAdpatationSBI/pull/21#issuecomment-5972414870)
for a clearer line between what belongs to a Model and what belongs to the Task or the
experiment. His points: a Model needs a specific set of Conditions and produces a
specific set of Observations on every Trial, and several Models can share them (the
one- and two-state Models need the same; COIN adds cues); Trial Types, Blocks, Schedule
Designs and Schedules are not specific to a Model; the same Task with different Schedule
Designs makes different Experiments; and `motor_sbi`, as a framework, should know as
little as possible about any of this.

**Decision** (terms as in the [glossary](../glossary.md)):

1. **Three kinds of module, each in its own directory under `src/`:**

   | Directory | Holds | Example |
   |---|---|---|
   | `src/designs/` | everything specific to a Task or an experiment design | `visuomotor_adaptation_task.py`, `visuomotor_adaptation_experiment.py` |
   | `src/models/` | everything specific to a Model | `one_state.py` |
   | `src/motor_sbi/` | the framework: code that works with any Model and any design | |

   All importable code lives under `src/`; the root-level `simulators/` goes.
2. **A Task module (`<task>_task.py`) holds only the Task's contract:**
   `CONDITION_VARS` (what a Schedule holds on every Trial) and `OBSERVATION_VARS` (what
   is recorded on every Trial). For visuomotor adaptation: `("p", "v")` and `("y",)`. It
   is everything a Model needs to know about the Task, and nothing else.
3. **An experiment module (`<task>_experiment.py`) holds what is needed to create
   Experiments of that Task:** the Trial Types, the Block structure, and the Schedule
   Designs with their Schedule Generators (for now one: the random Blocks of decision
   0005, `sample_schedule(rng, schedule_design)`), and possibly fixed Schedules. If a
   Task acquires several unrelated designs, how they are split across files is decided
   then.
4. **A Model module (`src/models/<model>.py`) holds only the Model:** `TASK` (the Task
   module it is written for), `PARAMETERS` (its parameters, in the order they have in a
   parameter vector; the one place that order is defined), its Prior Sampler
   `sample_prior(rng, size, prior)`, its Simulator `simulate_sitting(rng, theta,
   schedule)`, and later its Likelihood Function. It checks Schedules against
   `TASK.CONDITION_VARS`.
5. **No new classes.** Schedules are dicts of per-Trial arrays keyed by
   `CONDITION_VARS`; a Sitting adds the `OBSERVATION_VARS`. Ground Truth is a separate
   dict of parameter values and hidden states, never mixed into the Sitting. The Prior's
   and the Schedule Design's constants are passed whole, as one dict each, and checked
   on entry; the same dicts are saved with a Simulated Experiment's Ground Truth as the
   record of what produced it.
6. **`motor_sbi` uses only these names.** Its first function, written at the start of
   step C3 of [#12](https://github.com/opherdonchin/MotorAdpatationSBI/issues/12),
   simulates an Experiment for any Model and any Schedule Generator of the Model's Task:

   ```python
   simulate_experiment(rng, model, prior, schedule_generator, schedule_design, n_sittings)
   ```

   It draws parameter values with `model.sample_prior`, a Schedule for each Sitting
   with `schedule_generator`, and the movements with `model.simulate_sitting`, and
   returns the Sittings and, separately, their Ground Truth. It receives the Schedule
   Generator as an argument and never looks it up through the Model.
7. **Names.** Module-level contract names are in capitals, as structural fixed values:
   `CONDITION_VARS`, `OBSERVATION_VARS`, `PARAMETERS`, `TASK`, `TRIAL_TYPES`.

**Why:** The split follows ownership. A Task's contract is what Models share; an
experiment design is how Experiments of that Task are made; a Model is only its
parameters and Runnables. Putting each in its own directory makes the line between them
visible in the code, and lets a second Model of the same Task, or a second design for
it, be added without touching the others. Names and dicts carry the structure without
new machinery, stay close to how we talk about experiments, and are what BayesFlow
consumes. A framework that relies only on a handful of names can serve every Model.

*Alternatives:* frozen data classes for Schedules, Sittings, parameters and Ground Truth
(the first draft of this record; more structure than needed now); Condition names
declared by each Model (hides that Models share a Task); Trial Types and Schedule
Generators in the Model module (ties experiment design to one Model); the Model package
named `simulators` (it holds more than a Simulator); one keyword argument per constant
(the Prior and the Schedule Design stop being single things that can be passed on or
saved); a Model class (not until a second Model, or more generic code, shows what it
must contain); writing `simulate_experiment` now (no consumer until step C3).

**Consequences:**

- The code in [PR #18](https://github.com/opherdonchin/MotorAdpatationSBI/pull/18) is
  reorganized accordingly before it merges: `src/designs/visuomotor_adaptation_task.py`,
  `src/designs/visuomotor_adaptation_experiment.py` (Trial Types and `sample_schedule`),
  `src/models/one_state.py` (`TASK`, `PARAMETERS`, `sample_prior`, `simulate_sitting`),
  `simulators/` removed, `pyproject.toml` and the layout in `AGENTS.md` updated. Same
  seeds, same numbers.
- `designs`, `models` and `motor_sbi` are three top-level import names. They do not
  collide with anything installed today.
- Step C3 starts with `simulate_experiment` in `motor_sbi`.
