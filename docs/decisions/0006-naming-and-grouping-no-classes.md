# 0006 — Naming and grouping, not classes, for Models, Schedules and Sittings

**Date:** 2026-10-03 · **Status:** Proposed

**Context:** The one-state Runnables passed loosely related values: a Schedule as two
arrays side by side, parameter values as a 4-column array whose meaning depended on a
column order, and the Prior's constants as eight separate arguments. Opher
[asked](https://github.com/opherdonchin/MotorAdpatationSBI/pull/18#issuecomment-5968856811)
whether Models should be classes. A first proposal of data classes (this record's first
draft) was rejected as too much structure for a project looking for an easy win.
Opher's points: a Model needs a specific set of Conditions on every Trial, and that set
can be shared by several Models (the one- and two-state Models need the same; COIN adds
cues); Schedules and Sittings are not specific to a Model; the same Conditions with
different Schedule Designs make different Experiments; and `motor_sbi`, as a framework,
should know as little as possible about any of this.

**Decision** (terms as in the [glossary](../glossary.md)):

1. **No new classes.** The ideas are carried by names and by plain Python groupings.
2. **A Model's contract is three name lists** at the top of its module:
   `PARAMETER_NAMES` (the parameters, in the order they have in a parameter vector),
   `CONDITION_NAMES` (what a Schedule must hold on every Trial) and
   `OBSERVATION_NAMES` (what the Model produces on every Trial). For the one-state Model:
   `("A", "B", "sigma_eta", "sigma_epsilon")`, `("p", "v")` and `("y",)`.
   `PARAMETER_NAMES` is the one place where parameter order is defined.
3. **A Schedule is a dict of per-Trial arrays keyed by Condition names**, and a Sitting
   adds the Observation arrays. That is all `motor_sbi` will assume about a Sitting: a
   dict of equal-length per-Trial arrays. Which keys mean what is the Model's business.
4. **Definitions are passed whole.** The Prior Sampler takes the Prior's constants as
   one dict, `sample_prior(rng, size, prior)`, and the Schedule Generator takes the
   Schedule Design's constants as one dict, `sample_schedule(rng, schedule_design)`.
   Each checks the keys it receives on entry. The same dicts can be saved with a
   Simulated Experiment's Ground Truth as the record of what produced it.
5. **Experimental-design words.** A Schedule Design is written in terms of **Trial
   Types** (named combinations of Condition values: baseline, +1, -1, no vision) and
   Blocks (runs of one Trial Type). The one-state module lists them in `TRIAL_TYPES`.
6. **Where the Schedule Generator lives:** for now in the Model's module, though it is
   not specific to the Model. It moves to a shared place when a second Model needs it.
7. **Ground Truth** (step C3) is its own dict, parameter values and hidden states, never
   mixed into the Sitting.

**Why:** Names and dicts keep the code close to how we talk about experiments, add no
machinery, and are what BayesFlow consumes. The name lists make each Model's contract
visible and checkable (a Schedule with the wrong keys is rejected) and leave a clear
template for the next Model, without committing to a class design before a second Model
shows what is really shared.

*Alternatives:* frozen data classes for Schedules, Sittings, parameters and Ground Truth
(the first draft of this record; checked fields and a type for every idea, but more
structure than needed now); one keyword argument per constant (Python checks the names
for free, but the Prior and the Schedule Design stop being single things that can be
passed on or saved); a Model class (not until a second Model, or the first code that
works with any Model, shows what it must contain).

**Consequences:**

- The three one-state functions, their tests and the two working notebooks use this
  naming and grouping
  ([PR #18](https://github.com/opherdonchin/MotorAdpatationSBI/pull/18)); the notebooks'
  outputs are unchanged.
- Code that works with any Model reads the name lists rather than knowing a Model.
- When storage formats are aligned, the dicts are the natural starting point.
