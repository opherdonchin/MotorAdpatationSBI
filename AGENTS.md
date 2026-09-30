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

## Startup

- Read [docs/plan.md](docs/plan.md) and the latest `docs/journal/` entry.
- Keep durable state in repo files, not chat (see *Durable state files*).

## Where things live

Every file has a home. Do not create new top-level directories, or new kinds of
auxiliary files (plans, reports, exports, debug dumps), without asking.

```
AGENTS.md, CLAUDE.md, README.md
pyproject.toml, pixi.lock     # environment (pixi); never hand-edit the lock
src/motor_sbi/                # reusable, tested code: likelihoods, SBI wrappers, diagnostics
simulators/                   # model simulators; separate from the package
notebooks/                    # all work starts here (see *Notebooks*)
analyses/sim/<study>/         # one folder per simulated-data analysis
analyses/data/<dataset>/      # one folder per real-data analysis
tests/                        # pytest code tests (repo root, standard for a src layout)
docs/plan.md                  # the one living plan: current goals + next steps
docs/journal/YYYY-MM-DD.md    # session log
docs/decisions/NNNN-title.md  # decision records
docs/models/                  # model math; must match the code
Resources/                    # external background material (see #2)
```

- Large or regenerable outputs (simulation banks, trained networks, traces, figures from
  exploratory runs) go inside their analysis folder under `analyses/` and are
  gitignored. Each saved output records the root seed and git commit that produced it.
- Findings go in the journal or in a finalized notebook, not in ad hoc report files.

## Durable state files

### Plan — `docs/plan.md`

- **What:** current goals, current state, and the ordered next steps. Nothing else.
- **When to update:** whenever a goal, the state, or the next steps change; check it at the
  end of every session.
- **How:** rewrite in place; git history is the archive.
- **When to read:** at the start of every session.

### Journal — `docs/journal/YYYY-MM-DD.md`

- **What:** a factual log of each working session. One file per day; a second session on
  the same day adds a new `## Session N` section.
- **When to update:** at the end of each session, and immediately after any significant
  result or dead end (so it is not lost if the session breaks).
- **Format:**

  ```markdown
  # YYYY-MM-DD

  ## Session 1 — <topic>

  **Goal:** what we set out to do.
  **Done:** what changed, with links to commits, PRs, notebooks (and cell labels).
  **Results:** numbers and figures, each with the notebook/command that produced it.
  **Decisions:** one line each, linking to `docs/decisions/` records where one exists.
  **Permission points:** (independent work only) where permission would normally have
  been asked, and what was decided.
  **Open questions / next:** what is unresolved; update docs/plan.md to match.
  ```

- **When to read:** the latest entry at startup; earlier entries when resuming a thread
  of work (search by topic).
- Entries are history: do not rewrite past entries except to fix errors, and say so.

### Decision records — `docs/decisions/NNNN-short-title.md`

- **What:** choices that constrain future work and are not obvious from the code: tools,
  model formulations, conventions, rejected alternatives worth remembering.
- **When to write:** when the decision is made (drafted by the agent, accepted by Opher).
  Small choices go in the journal's *Decisions* line instead.
- **Format:**

  ```markdown
  # NNNN — <title>

  **Date:** YYYY-MM-DD · **Status:** Proposed | Accepted | Superseded by NNNN

  **Context:** the problem and constraints.
  **Decision:** what we chose.
  **Why:** the reasons, including alternatives considered.
  **Consequences:** what this commits us to or rules out.
  ```

- **Superseding:** write a new record and set the old one's status to `Superseded by
  NNNN`. Decision records are the one exception to "delete superseded files": the
  history of why is the point.
- **When to read:** before changing anything in an area a record covers (check titles
  with `ls docs/decisions`).

### Model math — `docs/models/`

- One file per model: equations, parameter meanings, units, domains, and the parameter
  order used in code. Update in the same change as the code it describes.

## Notebooks

- Everything starts as a notebook in `notebooks/`. Exploration notebooks are prefixed
  `explore_` and may be deleted once their result is captured elsewhere.
- Every success becomes a finalized notebook: well documented, easy to read, runs top to
  bottom from a clean kernel, no hidden state.
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

## Code rules that need discussion first

- **Classes are privileged.** Do not create a class (or class hierarchy) without
  discussing it with Opher first.
- **Helpers come from repetition.** A helper function comes into being only when the
  same code has been written twice, and its creation is discussed first.
- **Scientific tests are designed together.** When starting a study or simulator, propose
  which correctness checks it needs (exact likelihood, limiting cases, recovery, SBC…)
  and agree on them. Not every simulator needs the same checks.

Pytest code tests (`tests/`) are separate and can be written freely.

## Randomness

- One root seed per study or notebook, set once in the config cell and recorded with
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

## Working style

- Small, reviewable changes. Commit after each successful sub-step.
- Parameter order and transforms (e.g. constrained ↔ unconstrained) are defined in
  exactly one place.
- Prefer flat data structures and vectorized array operations over Python loops.
- Be honest in naming: a name must not promise more than the code does.
- Plain code first; no abstraction until there is a second use (see above).
- If an approach starts conflicting with these principles, stop and realign.

## Input checking (evolving policy)

This section grows as cases come up; add each new rule with a one-line reason.

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

- BayesFlow code: consult `amortized-workflow` before writing it.
- PyMC/ArviZ: `pymc-modeling`, `bayesian-workflow`, `arviz-diagnostics`,
  `prior-elicitation`.
- Figures: `dataviz`.

## Autonomy

- Proceed without asking on routine work: reads, searches, local edits, running
  notebooks and tests, normal git.
- Ask before: new classes or helpers (above), new directories or auxiliary file kinds,
  dependency changes, anything destructive or hard to undo, anything with external side
  effects (the GitHub repo is **public**).
- For non-obvious tradeoffs, explain briefly and choose the simpler, less stateful option.
- **Independent work.** When asked to work independently, keep going without asking for
  any permission, including destructive changes within the repo. Record every point where
  permission would normally have been asked, and what was decided, in the journal's
  *Permission points*.

## Git and GitHub

- Decide whether a piece of work needs its own branch. Say what you decided and commit
  any pending work before starting.
- Branch names are descriptive and easy to find: `<area>/<short-description>`, e.g.
  `setup/agent-instructions`, `sim/one-state-kalman`.
- Work done on `main` may be committed and pushed to `main`. Branches merge into `main`
  only with Opher's approval, through a pull request.
- Never stop work while waiting for a merge: continue on the branch, or start the next
  piece of work.
- PR descriptions say what changed, why, how it was verified, and what to look at.
- Commit messages explain why, not just what.
- All work must be recoverable on another machine: push working branches at least at the
  end of every session.
- Git history is the archive: delete superseded files rather than keeping `old` copies.
  Update or remove references in the same change.
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
- When you infer something or make a judgment call that affects the outcome, say so.
