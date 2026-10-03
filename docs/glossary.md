# Glossary

The words this project uses for the things it works with. A capitalized term (Sitting,
Experiment, Runnable) is used in exactly the sense defined here; the same word in lower
case is ordinary language and may be loose. Add a term here before relying on it.

The terms fall into five groups. Definitions say what something is mathematically.
Runnables are code that instantiates a Definition. Data is what Runnables take in and
produce. An Analysis uses a Runnable on data. A Check tests a Runnable or an Analysis.

How the work itself is organized (Issues, pull requests, the plan) is a separate matter
and has no terms here.

## The task and its data

**Task.** What a subject does and what can be manipulated. Here: reaching to a target
with cursor feedback, where the cursor can be rotated (a perturbation) or hidden. The Task
fixes what is recorded on each Trial and in what units.

**Trial.** One movement, with the perturbation and the vision condition in force on it.

**Block.** A run of consecutive Trials in the same condition.

**Schedule.** The condition on every Trial of one Sitting: for the one-state Model, the
perturbation $p_t$ and the vision flag $v_t$, Trial by Trial.

**Sitting.** One session of one subject, actual or simulated: a Schedule and the movement
recorded on every Trial. The unit a likelihood is computed for.

**Experiment.** A collection of Schedules for a Task, with the Sittings done on them.
An **Actual Experiment** was done by people. A **Simulated Experiment** has Sittings
produced by a Simulator, each simulated subject with its own parameter values.

## Definitions

Mathematical statements. They have no inputs and outputs of their own, so they cannot be
checked directly; their Runnables can.

**Model.** A generative description of how the movements of a Sitting arise from its
Schedule, given parameter values. It has no Prior. Example: the one-state Model,
[docs/models/one_state.md](models/one_state.md).

**Prior.** A distribution over a Model's parameters, chosen for a particular use.

**Schedule Design.** The rules for producing Schedules, for example those in
[decision 0005](decisions/0005-one-state-model-published-form.md).

**Inference Method.** A way of getting from Sittings to a Model's parameters, for
example the exact likelihood sampled with MCMC, or neural posterior estimation with
BayesFlow.

## Runnables

A **Runnable** (in full, a Runnable Instantiation of a Definition) is code with stated
inputs and outputs. One Definition can have several Runnables. Every Runnable is
Checkable. The common ones have short names:

| Runnable | Instantiates | Inputs | Outputs |
|---|---|---|---|
| **Simulator** | a Model, run forward | parameter values, a Schedule, a random generator | Sitting(s) |
| **Likelihood Function** | a Model, scored | a Sitting, parameter values | log-likelihood |
| **Prior Sampler** | a Prior | a random generator, a count | parameter values |
| **Schedule Generator** | a Schedule Design | a random generator | a Schedule |
| **Inference Engine** (or **Engine**) | an Inference Method | Sitting(s) | posterior draws, or a likelihood or likelihood ratio |

Two parameterizations of one PyMC model, the same PyMC model on two backends, and a
trained BayesFlow network are each a different Inference Engine. The first two share
one Inference Method.

## Analyses and Checks

**Analysis.** Running an Inference Engine on an Experiment. Its outputs (a posterior for
every Sitting) can be checked: against the true parameter values when the Experiment is
Simulated, or against another Analysis of the same Experiment.

**Check.** A comparison of what a Runnable or an Analysis produces with a result obtained
independently of it. Something is **Checkable** if it has stated inputs and outputs:
every Runnable, and every Analysis. Models, Priors, Schedule Designs and Inference Methods
are checked through their Runnables.
