# AGENTS.md — MotorAdaptationSBI

Single source of agent instructions for this repo. `CLAUDE.md` only points here.
This file holds slow-changing rules. Current goals and next steps live in
[docs/plan.md](docs/plan.md).

## Purpose

Turn motor-adaptation simulators into validated likelihoods or posteriors, using
simulation-based inference (SBI), that can be used in hierarchical Bayesian analyses of
real experiments.

Progress is measured by:

- **Accuracy:** parameter recovery and calibration, checked against exact references
  wherever they exist.
- **Reach:** the range of models handled, from linear state-space models toward
  context-inference models (COIN-class).
- **Use:** learned likelihoods that work inside hierarchical models (HSSM or PyMC).
- **Understanding:** every result reproducible from a finalized notebook and explainable
  by the humans on the team.

`Resources/privileged_state_sbi_proposal_v2.md` is background for ideas only. It is
neither a plan nor a guide; do not import its procedures unless asked.

## Process

The working process — scope issues, presentations, approval, the understanding map,
durable state files (plan, journal, decision records), autonomy and git workflow — is
defined in [docs/process.md](docs/process.md). Follow it. In this repo the reviewer is
Opher.

Project-specific settings for that process:

- The wiki is cloned into `wiki/` (gitignored) from
  `https://github.com/opherdonchin/MotorAdpatationSBI.wiki.git`.
- Branch name examples: `setup/agent-instructions`, `sim/one-state-kalman`.
- The GitHub repo is **public**: anything pushed, including issues and the wiki, is
  visible to everyone.

## Where things live

Every file has a home. Do not create new top-level directories, or new kinds of
auxiliary files (plans, reports, exports, debug dumps), without asking.

```
AGENTS.md, CLAUDE.md, README.md
.github/skills/                  # skills, templates and scripts (see docs/process.md)
.claude/                         # Claude Code: hooks, and a link to .github/skills
pyproject.toml, pixi.lock        # environment (pixi); never hand-edit the lock
src/                             # Where all importable source lives
   motor_sbi/                    # the framework: code that works with any Model and design
   models/<model>.py             # one Model: TASK, PARAMETERS, Prior Sampler, Simulator
   designs/                      # all experimental designs from task specification through schedules
      <task>_task.py             # a Task's contract: CONDITION_VARS, OBSERVATION_VARS
      <task>_experiment.py       # Trial Types, Schedule Designs, Schedule Generators
notebooks/                       # All .ipynb jupyter notebooks
   <model>_<topic>.ipynb         # finalized notebooks (see *Notebooks*)
   working/                      # notebooks in progress; committed, pruned when stale
data/                            # Experiments: Schedules and Sittings; gitignored (storage: #3)
  actual/<experiment>/           #   Actual Experiments
  simulated/<experiment>/        #   Simulated Experiments, with their Ground Truth
outputs/<model>/                 # everything else notebooks save; gitignored, regenerable
  engines/<name>/                #   trained Inference Engines
  analyses/<name>/               #   results of Analyses
tests/                           # pytest code tests (repo root, standard for a src layout)
docs/                            # documentation: process, state, decisions, terms, models
  process.md                     #   the working process (generic)
  plan.md                        #   the one living plan: current goals + next steps
  journal/YYYY-MM-DD.md          #   session log
  decisions/NNNN-title.md        #   decision records
  glossary.md                    #   the project's terms (Sitting, Experiment, Runnable...)
  models/<model>.md              #   one page per Model (see *Model pages*)
  experiments/<experiment>.md    #   one page per Actual Experiment, when we have one
Resources/                       # background material; moving to the wiki (#2)
wiki/                            # gitignored clone of the GitHub wiki
```

- Words: [docs/glossary.md](docs/glossary.md). `<model>` is a Model's short name
  (`one_state`); `<experiment>` and `<name>` are short, lowercase, with underscores, and
  are the same as the heading of the page section that describes them.
- An Experiment is its Schedules and its Sittings, and both live in `data/`. Simulated
  Experiments are stored and handled exactly like Actual ones, so that Inference Engines
  and Analyses stay blind to where their data came from. The one difference is the
  Ground Truth of a Simulated Experiment, which the Simulator produces and which is
  saved alongside the Sittings, apart from them; Analyses do not read it, Checks do.
- Everything else a notebook saves (trained Inference Engines, results of Analyses)
  goes under `outputs/<model>/`.
- Everything under `data/simulated/` and `outputs/` is gitignored and must be
  regenerable by re-running a notebook; each saved file records the root seed and the
  git commit that produced it. `data/actual/` is gitignored too. Data and outputs too
  expensive to regenerate: #3. Storage formats are not fixed yet; they will be aligned
  once there is more experience.
- Folders under `data/` and `outputs/` have no README; the page that describes them
  says what is in them (a model page, or the page of an Actual Experiment).
- What goes in `src/designs/`, `src/models/` and `src/motor_sbi/`, and the names each
  module provides: [decision 0006](docs/decisions/0006-models-tasks-and-designs.md).
- Schedule Designs are Definitions: they are described on a model page or the page of
  an Actual Experiment (or in a decision record) and implemented by a Schedule Generator
  in `src/designs/`.
- Findings go in the journal, a page in `docs/`, or a finalized notebook, not in ad hoc
  report files.

## Model pages — `docs/models/<model>.md`

One page per Model, so that a Model and everything done with it can be read in one place.
Its sections, in this order:

1. **The Model:** source, equations, parameter meanings, units, domains, and the
   parameter order used in code. Updated in the same change as the code it describes.
2. **Derived properties:** results that follow from the Model and serve as Checks.
3. **Likelihood:** the exact Likelihood Function, when there is one.
4. **Experiments, Inference Engines and Analyses** done with the Model, one subsection
   each: what it is (Prior and Schedule Design for a Simulated Experiment), the
   question, the notebook, the folder, and the result in a few lines. An Analysis of an
   Actual Experiment links to that Experiment's page. (Whether Simulated Experiments
   are described on model pages or experiment pages is open; for now, model pages.)

Nothing about a Model's work gets a separate file unless the page becomes too long to
read, and then only after asking.

## Notebooks

- Everything starts as a working notebook in `notebooks/working/`. Working notebooks are
  committed, on branches and on `main`, so work continues across computers and can span
  several branches.
- When a branch is created, the agent creating it decides which working notebooks are
  useful there and removes the rest on the branch. After a merge, working notebooks that
  have become stale may be removed from `main` in a separate commit. Their history stays
  in git.
- A success becomes a finalized notebook in `notebooks/`: well documented, easy to read,
  runs top to bottom from a clean kernel, no hidden state. Several working notebooks may
  be combined into one finalized notebook, and not every working notebook is finalized.
- Notebooks also document feature usage (how to use a simulator or wrapper).
- **Cell labels.** Every code cell starts with a comment label: a short, stable slug in
  brackets, e.g. `# [sim-train-bank] Simulate the training bank`. Section headings in
  markdown cells carry a label the same way. Refer to cells as
  `notebook.ipynb#[label]` in chat, journal and PRs. Labels are unique within a notebook
  and never renumbered; when a cell's purpose changes, change its label. (Jupyter's
  built-in cell ids are random and hidden in most editors, so they are not used for this.)
- When editing `.ipynb`, preserve outputs and execution counts of unedited cells. Do not
  save validation-run outputs unless asked.
- Math: `$$ ... $$` for display, `$ ... $` inline.
- Keep the statistical model visible: prior constants in a dedicated cell, named
  `{prior_param}_{likelihood_param}` (e.g. `mu_mu`, `sigma_mu`), ASCII names. Build the
  model in one cell and sample in a later cell.
- A constant in a config cell is either self-documenting (its name and value say what it
  sets) or has a comment saying what it sets and why it has that value. No comment that
  only repeats the code, and none that only names a section ("check 1").

## Code rules that need discussion first

- **Classes are privileged.** Do not create a class (or class hierarchy) without
  discussing it with Opher first.
- **Helpers come from repetition.** A helper function comes into being only when the
  same code has been written twice, and its creation is discussed first.
- **Scientific tests are designed together.** When starting a Runnable or an Analysis,
  propose which Checks it needs (exact likelihood, limiting cases, recovery, SBC…) and
  agree on them. Not every Runnable needs the same Checks.

Pytest code tests (`tests/`) are separate and can be written freely.

## Randomness

- One root seed per notebook, set once in the config cell and recorded with
  every saved output. Generate new root seeds with `secrets.randbits(128)`; do not use
  magic numbers like `42`.
- Use `np.random.default_rng(root_seed)`. Never use `np.random.seed` or other global
  RNG state.
- Functions that need randomness take an `rng: np.random.Generator` argument (SPEC 7
  name) and never construct their own.
- Separate purposes get separate streams via `rng.spawn(n)` (e.g. training / validation /
  test simulations), so changing one does not change the others. Never derive seeds as
  `seed + i`.
- Keras/BayesFlow: call `keras.utils.set_random_seed` once with an int drawn from the
  root stream. GPU training is reproducible to tolerance, not bit for bit.
- PyMC: pass the generator, `pm.sample(random_seed=rng)`.

## Working style and repo hygiene

What keeps the repo possible to hold in one's head. The `digest` skill audits the repo
against this section and against *Where things live*, *Notebooks*, *Code rules that
need discussion first* and *Data and provenance*. A new habit is added to whichever of
those sections it belongs to, and nowhere else.

- No stale files: nothing superseded, unreferenced, or describing a state that no
  longer holds. That includes documents. Working notebooks in use are not stale; see *Notebooks*
  for when they are pruned.
- What code does must be visible without digging through boilerplate.
- Every function has a full docstring: each input with its type, shape and meaning;
  which inputs are optional and their defaults; each return value with its type, shape
  and meaning; what the function does to get from one to the other; and whether it has
  state or side effects (advancing a random generator it was given is one).
- Small, reviewable changes. Commit after each successful sub-step.
- Parameter order and transforms (e.g. constrained ↔ unconstrained) are defined in
  exactly one place.
- Prefer flat data structures and vectorized array operations over Python loops.
- Be honest in naming: a name must not promise more than the code does.
- Names follow PEP 8: `snake_case` for variables, functions and arguments (notebook
  settings included), `CapWords` for classes. `UPPER_CASE` is used sparingly, by
  judgement, only to make a structural fixed value stand out (`OUT_DIR`,
  `PARAMETER_NAMES`); readability decides. The one exception to PEP 8: a symbol of a
  Model's equations keeps its case, alone or as a suffix (`A`, `mu_logit_A`), so code
  reads like the math. `ruff` enforces the rest; the exceptions are listed by name in
  `pyproject.toml`.
- Import modules, not the names inside them, and call through the module, so that every
  call shows where it comes from: `import numpy as np`, then `np.exp`;
  `from scipy import special`, then `special.expit`; `from models import one_state as
  mdl`, then `mdl.simulate_sitting`. Common libraries keep their usual aliases (`np`,
  `pd`, `plt`, `pm`, `az`, `bf`). Our own modules are aliased by role: `mdl` for a Model,
  `des` for an experiment design, `tsk` for a Task, so code reads the same whichever
  Model or design it uses.
- Plain code first; no abstraction until there is a second use (see above).
- If an approach starts conflicting with these principles, stop and realign.

## Input checking (evolving policy)

This section grows as cases come up. New rules are discussed with Opher first, then
added here with a one-line reason as soon as they are decided.

- Check inputs once, at the public boundary of a module (a simulator or likelihood entry
  point): shapes, parameter domains, schedule lengths. Inside, trust them.
- Invalid input raises immediately with a message naming the argument and the violated
  condition. Never clip, fill, or silently repair.
- No defensive checks for what the calling layer already guarantees.

## Use native tools

- Use the native approach of PyMC, ArviZ, PyTensor, BayesFlow and HSSM rather than
  handwritten code or other toolboxes.
- Research the current native way to do something (current docs, the skills below)
  before writing it. Do not rely on habit or memory of how it used to be done. The aim
  is a compact, self-contained code base.
- Pin fast-moving Bayesian/ML packages (BayesFlow, Keras, JAX, PyMC, HSSM) and update
  pins deliberately as a repo-wide task.

## Skills

- Process skills: see [docs/process.md](docs/process.md), *How the tooling works*.
- Starting a notebook: `new-notebook` (project-specific; lives with the others).
- BayesFlow code: consult `amortized-workflow` before writing it.
- PyMC/ArviZ: `pymc-modeling`, `bayesian-workflow`, `arviz-diagnostics`,
  `prior-elicitation`.
- Figures: `dataviz`.

## Data in git

- Never commit large data, trained weights, credentials, or regenerable outputs. How to
  store outputs that are too expensive to regenerate is an open question (#3).

## Environment

- pixi, Python 3.12, manifest in `pyproject.toml`. Run everything through `pixi run`.
  Never install into system Python. Re-lock after dependency changes.
- Keras backend: JAX.

## Data and provenance

- State which notebook or command produced each material number. Label one-off
  calculations as such.
- If the documented workflow fails, stop, diagnose and report; do not quietly create a
  replacement path.
- Derived outputs are not an independent check on their own source.

## Secrets

- Never put API keys, tokens or passwords in tracked files, logs, tests or docs.
- Do not open or modify files that appear to hold credentials; flag them and ask.

## Communication

- Lead with the result. Use repo-relative links when referencing files.
- Use the terms of [docs/glossary.md](docs/glossary.md) in their defined sense, and add a
  term there before relying on it.
- When you infer something or make a judgment call that affects the outcome, say so.
