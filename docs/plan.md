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
- Stage 1 of #12: steps C1 (the Simulator) and C2 (Prior and Schedule Design) merged,
  with the code in the layout of decision
  [0006](decisions/0006-models-tasks-and-designs.md): `src/designs/`, `src/models/`.
- Wiki drafts waiting for Opher: `Code-one-state-model`,
  `Code-visuomotor-adaptation-designs`, `Code-environment` (updated), `Concept-vocabulary`.
- The project's terms are in `docs/glossary.md`; the layout in `AGENTS.md` follows them
  (PR #19, merged). Wiki: `Concept-vocabulary` (draft).
- Official pymc-extras 0.15.1 works with the pinned PyMC 6.3 and reproduced the
  one-state likelihood in a one-off test; proposed to Opher as the exact reference for
  stage 2 (a dependency and a class, so not added without his agreement).
- Open issues: resources in the wiki (#2), large-data storage policy (#3),
  BayesFlow/HSSM numpy conflict (#4), multicore PyMC sampling across platforms (#9),
  live test of the compaction hooks (#10), hooks for Copilot and Codex (#11),
  sequential training and fitting in BayesFlow and PyMC (#23).

## Next steps

1. Step C3 of #12, one method per PR:
   - C3a: `simulate_experiment` in `motor_sbi`, and saving a Simulated Experiment (Sittings
     and Ground Truth apart) under `data/simulated/`; in review as PR #22.
   - C3b: background on amortized inference (concept page), then a BayesFlow posterior
     estimator trained on a Simulated Experiment, with BayesFlow's own recovery and
     calibration diagnostics.
   - C3c: the likelihood-ratio estimator.
2. Stage 2 of #12, validation by independent means: brute-force likelihood; Kalman
   filter; exact fits in PyMC; the lab's `pymc_extras` model brought up to date.
3. Decide the PyMC sampler setup for notebooks: test multicore sampling alongside JAX
   on each platform (Linux with GPUs, Windows without) (#9).
4. Test the compaction hooks in a live compaction (#10); Opher triggers `/compact`.
5. Hooks for other agents: instructions and configuration for Copilot and Codex (#11).
