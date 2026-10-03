---
name: new-notebook
description: Start a new notebook - for a Simulated Experiment, a trained Inference Engine, an Analysis, or the Checks of a Runnable - with its Checks agreed, a seeded config cell, output provenance and labelled cells, and a section on its model page. Use when the reviewer wants to start any new piece of notebook work.
---

# New notebook

Rules: `AGENTS.md` (*Where things live*, *Model pages*, *Notebooks*, *Randomness*,
*Code rules that need discussion first*); words: `docs/glossary.md`. This skill is only
the order of operations.

1. **Agree first.** The work needs an agreed scope (`scope` skill), and the Checks it will
   run are agreed with the reviewer. Agree the names too: the Model's short name and a
   short topic (`one_state_priors`).
2. **Create `notebooks/<model>_<topic>.ipynb`** (prefix `explore_` while exploring),
   starting with:
   - a markdown title cell: the question, the scope issue, the agreed Checks;
   - `# [imports]`;
   - `# [config]`: the root seed and every constant. Generate the seed once with
     `python -c "import secrets; print(secrets.randbits(128))"` and paste the integer in;
   - `# [rng]`: the root generator and one spawned stream per purpose.
3. **If the notebook saves anything,** add the three provenance lines to `[config]` and
   save both values with every file:

   ```python
   REPO = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip())
   GIT_COMMIT = subprocess.check_output(["git", "describe", "--always", "--dirty"], text=True).strip()
   OUT_DIR = REPO / "outputs" / "<model>" / "<experiments|engines|analyses>" / "<name>"
   ```

   `REPO` is the repository's top folder, so the notebook finds it from anywhere.
   `GIT_COMMIT` is the commit that produced the output, with `-dirty` if there were
   uncommitted changes; commit before a run whose outputs matter. `OUT_DIR` is where
   this notebook's outputs go.
4. **Describe it on the model page:** a subsection under *Experiments, Inference Engines
   and Analyses* with the same `<name>`.
5. **Record it:** the plan and the journal (`journal` skill).
6. **When it works,** it becomes a finalized notebook (no `explore_` prefix).
