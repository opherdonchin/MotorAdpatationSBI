---
name: new-analysis
description: Start a new analysis (a study on simulated data, or of a real dataset) - agree its correctness checks, create its folder and its exploration notebook with a seeded config cell and labelled cells. Use when the reviewer wants to start a new study, simulation experiment, or data analysis.
---

# New analysis

Rules: `AGENTS.md` (*Where things live*, *Notebooks*, *Randomness*, *Code rules that
need discussion first*). This skill is only the order of operations.

1. **Agree first.** A new analysis needs a scope issue (`scope` skill). In *Done when*,
   propose the correctness checks for this analysis and agree them with the reviewer.
   Agree the name too: short, lowercase, underscores (`one_state`).
2. **Create the folder:** `analyses/sim/<name>/` or `analyses/data/<name>/`, with a
   `README.md` (the question, a link to the scope issue, the agreed checks). Make sure
   `.gitignore` excludes what the analysis will generate there.
3. **Create `notebooks/explore_<name>.ipynb`** starting with:
   - a markdown title cell: the question, the scope issue, the agreed checks;
   - `# [config]`: the root seed and every constant, and the output folder. Generate the
     seed once with `python -c "import secrets; print(secrets.randbits(128))"` and paste
     the integer in;
   - `# [rng]`: the root generator and one spawned stream per purpose;
   - `# [imports]`.
4. **Record it:** add the analysis to `docs/plan.md` and the journal (`journal` skill).
5. **When it works,** it becomes a finalized notebook (no `explore_` prefix).
