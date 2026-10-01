# Plan

Current goals and next steps. Rewritten in place; see git history for earlier versions.

## Current goals

1. **Quick win: BayesFlow parameter recovery on a one-state model.** A one-state
   motor-adaptation state-space model with state and output noise,

   ```math
   x_{t+1} = A\, x_t + B\,(p_t - y_t) + \eta_t,\qquad y_t = x_t + \varepsilon_t
   ```

   with $\eta_t \sim \mathcal N(0,\sigma_x^2)$ and $\varepsilon_t \sim \mathcal N(0,\sigma_y^2)$,
   on random perturbation schedules of varying length (blocks of 0, +1 or -1). BayesFlow
   learns a likelihood-to-evidence ratio (NRE); success is agreement with the exact
   Kalman likelihood and good parameter recovery and calibration.
2. **Next quick win:** the same learned likelihood used inside HSSM for a small
   hierarchical fit.
3. **Side project:** a working process that keeps the human fully in the loop and
   produces shareable documentation as a byproduct.

## Current state

- Process: [docs/process.md](process.md); project rules: [AGENTS.md](../AGENTS.md).
- Environment built and tested (pixi, GPU JAX, BayesFlow, PyMC).
- Human-in-the-loop toolkit built (scope #5 closed): skills, templates, scripts and
  hooks in `.github/skills/` and `.claude/`; wiki skeleton live.
- Wiki: both code pages (`Code-environment`, `Code-process-scripts`) are `understood`;
  no understanding debt.
- Decision [0002](decisions/0002-one-state-model.md) (one-state model, priors, random
  schedules) is accepted.
- Scope #12 (`one_state` analysis) is agreed. PR 1 (#13, `sim/one-state-kalman`) is
  ready for review: simulator and exact Kalman likelihood in modules, model math in
  [docs/models/one_state.md](models/one_state.md), and
  `notebooks/one_state_exact.ipynb` with checks 1 to 4 passing.
- Open issues: resources in the wiki (#2), large-data storage policy (#3),
  BayesFlow/HSSM numpy conflict (#4), multicore PyMC sampling across platforms (#9),
  live test of the compaction hooks (#10), hooks for Copilot and Codex (#11).

## Next steps

1. Opher reviews PR #13 (full track proposed) and agrees or changes the tolerances it
   proposes for PR 2.
2. PR 2 of #12 (`sbi/one-state-nre`): the BayesFlow ratio estimator, checked against
   the exact reference.
3. Decide the PyMC sampler setup for notebooks: test multicore sampling alongside JAX
   on each platform (Linux with GPUs, Windows without) (#9).
4. Test the compaction hooks in a live compaction (#10); Opher triggers `/compact`.
5. Hooks for other agents: instructions and configuration for Copilot and Codex (#11).
