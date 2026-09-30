# AGENTS.md — MotorAdaptationSBI

Single source of agent instructions for this repo. `CLAUDE.md` only points here.

## What this project is

Simulation-based inference (BayesFlow, later HSSM/PyMC) for motor-adaptation models.
Current goal: a quick win — BayesFlow recovers the parameters of a one-state
state-space model (state + output noise), checked against an exact Kalman likelihood.
Next quick win: the same learned likelihood consumed by HSSM.

`Resources/privileged_state_sbi_proposal_v2.md` is background for ideas only. It is
neither a plan nor a guide; do not import its procedures unless asked.

## Startup

- Read `docs/plan.md` (current state and next steps) and the latest `docs/journal/` entry.
- Keep durable state in repo files, not chat. Record decisions, commitments and status
  changes in the right file (see *Where things live*) as they happen.

## Where things live

Every file has a home. Do not create new top-level directories, or new kinds of
auxiliary files (plans, reports, exports, debug dumps), without asking.

```
AGENTS.md, CLAUDE.md, README.md
pyproject.toml, pixi.lock     # environment (pixi); never hand-edit the lock
src/motor_sbi/                # reusable, tested code: likelihoods, SBI wrappers, diagnostics
simulators/                   # model simulators; separate from the package
notebooks/                    # all work starts here (see *Notebooks*)
data/simulations/<study>/     # one folder per simulated-data study
data/experiments/<dataset>/   # one folder per real experimental dataset
tests/                        # pytest code tests only
docs/plan.md                  # the one living plan: current state + next steps
docs/journal/YYYY-MM-DD.md    # session log: what we tried, results, open questions
docs/decisions/NNNN-title.md  # short decision records (context, choice, why)
docs/models/                  # model math; must match the code
Resources/                    # external background material
```

- Large or regenerable outputs (simulation banks, trained networks, traces, figures from
  exploratory runs) go inside their study folder under `data/.../<study>/` and are
  gitignored. Each saved output records the root seed and git commit that produced it.
- Findings go in the journal or in a finalized notebook — not in ad hoc report files.
- There is one plan file. Rewrite it in place; git history is the archive.

## Notebooks

- Everything starts as a notebook in `notebooks/`. Exploration notebooks are prefixed
  `explore_` and may be deleted once their result is captured elsewhere.
- Every success becomes a finalized notebook: well documented, easy to read, runs top to
  bottom from a clean kernel, no hidden state.
- Notebooks also document feature usage (how to use a simulator or wrapper).
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
- Fail fast. Validate once at a clear boundary, then trust the result; no defensive code
  for what the caller already guarantees.
- Parameter order and transforms (e.g. constrained ↔ unconstrained) are defined in
  exactly one place.
- Prefer flat data structures and vectorized array operations over Python loops.
- Be honest in naming: a name must not promise more than the code does.
- Plain code first; no abstraction until there is a second use (see above).
- If an approach starts conflicting with these principles, stop and realign.

## Autonomy

- Proceed without asking on routine work: reads, searches, local edits, running
  notebooks and tests, normal git on a working branch.
- Ask before: new classes or helpers (above), new directories or auxiliary file kinds,
  dependency changes, anything destructive or hard to undo, anything with external side
  effects (the GitHub repo is **public**).
- For non-obvious tradeoffs, explain briefly and choose the simpler, less stateful option.

## Git and GitHub

- Decide whether a piece of work needs its own branch. Say what you decided and commit
  any pending work before starting.
- Branch names are descriptive and easy to find: `<area>/<short-description>`, e.g.
  `setup/agent-instructions`, `sim/one-state-kalman`.
- Changes reach `main` through pull requests. Opher reviews and merges; never merge or
  push to `main`.
- PR descriptions say what changed, why, how it was verified, and what to look at.
- Commit messages explain why, not just what.
- Git history is the archive: delete superseded files rather than keeping `old` copies.
  Update or remove references in the same change.
- Never commit large data, trained weights, credentials, or regenerable outputs.

## Environment

- pixi, Python 3.12, manifest in `pyproject.toml`. Run everything through `pixi run`.
  Never install into system Python. Re-lock after dependency changes.
- Pin fast-moving Bayesian/ML packages (BayesFlow, Keras, JAX, PyMC, HSSM) and update
  pins deliberately as a repo-wide task.
- Keras backend: JAX.

## Skills

- BayesFlow code: consult `amortized-workflow` before writing it.
- PyMC/ArviZ: `pymc-modeling`, `bayesian-workflow`, `arviz-diagnostics`,
  `prior-elicitation`. Prefer current native APIs over custom code.
- Figures: `dataviz`.

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
