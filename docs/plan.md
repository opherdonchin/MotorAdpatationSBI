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
   first learns the posterior directly, to see early whether the parameters can be
   recovered, and then a likelihood-to-evidence ratio (NRE), which is what hierarchical
   models need. Success is good parameter recovery and calibration, and agreement with
   the exact Kalman likelihood, which is built afterwards as an independent check.
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
- Decision [0002](decisions/0002-one-state-model.md) (one-state model) is marked
  accepted but under revision: its math does not draw on GitHub, and Opher's review
  raised the model form, the identifiability statement and the schedule design.
- Scope #12 (`one_state` analysis): the first attempt, PR #13, was closed unmerged as too
  large and too fast. Its code (simulator, Kalman likelihood, exact-posterior checks) is
  on the branch `sim/one-state-kalman`, unmerged. The scope was changed on the issue and
  agreed: one method per PR, background first; BayesFlow on the simulations before the
  exact machinery, which becomes a separate validation stage.
- Decision [0005](decisions/0005-one-state-model-published-form.md) (accepted) fixes the
  model, priors and schedules; it supersedes 0002.
- Stage 1 of #12: step C1 (the simulator) merged; step C2 (prior and schedules) ready
  for review as PR #18.
- Official pymc-extras 0.15.1 works with the pinned PyMC 6.3 and reproduced the
  one-state likelihood in a one-off test; proposed to Opher as the exact reference for
  stage 2 (a dependency and a class, so not added without his agreement).
- Open issues: resources in the wiki (#2), large-data storage policy (#3),
  BayesFlow/HSSM numpy conflict (#4), multicore PyMC sampling across platforms (#9),
  live test of the compaction hooks (#10), hooks for Copilot and Codex (#11).

## Next steps

1. Opher reviews PR #18 (step C2), including his judgement of the generated sittings.
2. Step C3 of #12 then starts: BayesFlow on the simulations, learning the posterior first,
   with the output-provenance lines explained and given a wiki page.
3. Stage 2 of #12, validation by independent means: brute-force likelihood; Kalman
   filter; exact fits in PyMC; the lab's `pymc_extras` model brought up to date.
4. Decide the PyMC sampler setup for notebooks: test multicore sampling alongside JAX
   on each platform (Linux with GPUs, Windows without) (#9).
5. Test the compaction hooks in a live compaction (#10); Opher triggers `/compact`.
6. Hooks for other agents: instructions and configuration for Copilot and Codex (#11).
