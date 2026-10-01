---
name: new-analysis
description: Start a new analysis (a study on simulated data, or of a real dataset) - agree its correctness checks, create its folder and its exploration notebook with a seeded config cell and labelled cells. Use when the reviewer wants to start a new study, simulation experiment, or data analysis.
---

# New analysis

An analysis has a folder for what it produces and starts as an exploration notebook.
The layout, notebook, randomness and code rules are in `AGENTS.md`; follow them. This
skill is the order of operations.

## 1. Agree before creating anything

A new analysis is nontrivial work: it needs a scope issue (`scope` skill). In the
issue's *Done when*, propose the **correctness checks** for this analysis and agree
them with the reviewer. Not every analysis needs the same checks; pick from, and add to:

- an exact or reference result to compare against;
- limiting cases with known answers;
- parameter recovery on simulated data;
- calibration (simulation-based calibration, coverage);
- sensitivity to the choices most likely to matter.

Also agree the analysis name: short, lowercase, underscores (`one_state`).

## 2. Create the folder

- Simulated data: `analyses/sim/<name>/`. Real data: `analyses/data/<name>/`.
- Add `analyses/.../<name>/README.md`: one paragraph on the question, a link to the
  scope issue, and the agreed checks. This is the only tracked file there to begin with.
- Everything the analysis generates (simulation banks, trained networks, traces,
  figures) goes in this folder and is gitignored. Check `.gitignore` covers it; add a
  rule if not.

## 3. Create the exploration notebook

`notebooks/explore_<name>.ipynb`, with these cells first:

1. A markdown title cell: the question, the scope issue, the agreed checks.
2. `# [config]` — the root seed and every constant:
   - generate the seed once with `python -c "import secrets; print(secrets.randbits(128))"`
     and paste the integer in; never reuse a seed from another notebook;
   - the output folder path; the git commit is read at run time.
3. `# [rng]` — `rng = np.random.default_rng(ROOT_SEED)`, then one spawned stream per
   purpose (`rng.spawn(n)`).
4. `# [imports]`.

Every code cell starts with a `# [label]` comment; labels are unique and stable.

## 4. Record it

Add the analysis to `docs/plan.md` and note the start in the journal (`journal` skill).

## When it succeeds

An exploration that works becomes a finalized notebook (no `explore_` prefix): runs top
to bottom from a clean kernel, documented, easy to read. Code written twice becomes a
helper only after discussing it with the reviewer.
