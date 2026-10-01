# Plan

Current goals and next steps. Rewritten in place; see git history for earlier versions.

## Current goals

1. **Quick win: BayesFlow parameter recovery on a one-state model.** A one-state
   motor-adaptation state-space model with state and output noise,

   ```math
   x_{t+1} = A\, x_t + B\,(p_t - y_t) + \eta_t,\qquad y_t = x_t + \varepsilon_t
   ```

   with $\eta_t \sim \mathcal N(0,\sigma_x^2)$ and $\varepsilon_t \sim \mathcal N(0,\sigma_y^2)$,
   on a fixed perturbation schedule. BayesFlow learns a likelihood-to-evidence ratio
   (NRE); success is agreement with the exact Kalman likelihood and good parameter
   recovery and calibration.
2. **Next quick win:** the same learned likelihood used inside HSSM for a small
   hierarchical fit.
3. **Side project:** a working process that keeps the human fully in the loop and
   produces shareable documentation as a byproduct.

## Current state

- Process: [docs/process.md](process.md); project rules: [AGENTS.md](../AGENTS.md).
- Environment built and tested (pixi, GPU JAX, BayesFlow, PyMC).
- Human-in-the-loop toolkit built (scope #5 closed): skills, templates, scripts and
  hooks in `.github/skills/` and `.claude/`; wiki skeleton live.
- Wiki pages waiting for Opher: `Code-environment` (draft), `Code-process-scripts`
  (needs-review; understanding debt #8).
- Open issues: resources in the wiki (#2), large-data storage policy (#3),
  BayesFlow/HSSM numpy conflict (#4), understanding debt for `wiki_status.py` (#8).

## Next steps

1. Start a new session to see the automatic orientation working.
2. Opher reads and edits the two wiki pages; that clears #8.
3. Confirm the open points of decision 0002 (initial state, parameter domains, schedule).
4. One-state analysis: scope issue with agreed correctness checks (`new-analysis`
   skill), then `notebooks/explore_one_state.ipynb` with outputs under
   `analyses/sim/one_state/`.
5. Decide the PyMC sampler setup for notebooks (fork warning with JAX; nutpie?).
