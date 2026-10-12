# Plan

Current goals and next steps. Rewritten in place; see git history for earlier versions.

**Rewritten 2026-10-12, and not yet confirmed by Opher.** The earlier plan made
agreement with the exact Kalman likelihood part of the first goal and put a fit in HSSM
second. On 2026-10-11 Opher chose the two-state Model as the next step and said the
comparison with exact answers interests him less for now. The goals below follow that.
The order of goals 2 and 3 after the two-state work is my proposal.

## Current goals

We are finding out whether the whole approach is feasible: simulation-based inference
with BayesFlow, for motor-adaptation Models, ending in hierarchical analyses. Validated
answers come after that, and what is skipped on the way is listed under *Debt*.

1. **Posterior networks are feasible for our Models.** A network trained once on
   simulated Sittings gives a calibrated posterior for a new Sitting, at a cost in time
   and memory we can afford.
   - One-state Model: done
     ([notebooks/one_state_posterior.ipynb](../notebooks/one_state_posterior.ipynb)).
   - Two-state Model: in progress
     ([issue #28](https://github.com/opherdonchin/MotorAdpatationSBI/issues/28)).
2. **A learned likelihood is feasible, and usable in a hierarchical fit.** A
   likelihood-to-evidence ratio estimator (NRE) for the one-state Model, then that
   estimator inside HSSM or PyMC for a small hierarchical fit. This is the project's
   purpose (*Use* in [AGENTS.md](../AGENTS.md)) and the part not yet tried.
3. **Validation against exact answers.** The one-state and two-state Models are linear
   and Gaussian, so a Kalman filter gives their exact likelihood. Deferred; see *Debt*.
4. **Side project:** a working process that keeps the human fully in the loop and
   produces shareable documentation as a byproduct.

## Current state

- Process: [docs/process.md](process.md); project rules: [AGENTS.md](../AGENTS.md).
  Environment built and tested (pixi, GPU JAX, BayesFlow, PyMC).
- One-state Model ([docs/models/one_state.md](models/one_state.md), decisions
  [0005](decisions/0005-one-state-model-published-form.md),
  [0006](decisions/0006-models-tasks-and-designs.md),
  [0007](decisions/0007-summary-network-for-sittings.md), all accepted): Simulator,
  Prior, Schedule Design, Simulated Experiments and a posterior network. Recovery is
  good for all four parameters and calibration passes, narrowly for `B`. Not compared
  with an exact posterior.
- Two-state Model ([issue #28](https://github.com/opherdonchin/MotorAdpatationSBI/issues/28), agreed; its *Done when* rewritten
  2026-10-12 around feasibility, convergence and calibration):
  - [PR #29](https://github.com/opherdonchin/MotorAdpatationSBI/pull/29): decision record 0008, revised after Opher's review (his
    ranges for the four rates, translated step by step; code names `Af`, `As`, `Bf`,
    `Bs`, `s_eta`, `s_epsilon`). Compared with the lab's
    code, with his permission. Waiting for him.
  - [PR #30](https://github.com/opherdonchin/MotorAdpatationSBI/pull/30), built on #29: Simulator, Prior Sampler, their Checks (all
    pass) and the Model page, brought in line with the revised record. Opher reviews
    it after #29.
- [PR #33](https://github.com/opherdonchin/MotorAdpatationSBI/pull/33): the process rule for debt (below). Waiting for Opher.
- Scope [#12](https://github.com/opherdonchin/MotorAdpatationSBI/issues/12) (`one_state` analysis) is still open. Its step C3c (the
  likelihood-ratio estimator) is goal 2 here; its stage 2 (validation) is goal 3 and is
  recorded as debt. The issue should be rewritten or split to match this plan.
- Wiki. Waiting for Opher: drafts `Concept-two-state-model` (part of PR #29),
  `Guide-one-state-model`, `Code-visuomotor-adaptation-designs`, `Code-environment`,
  `Code-one-state-posterior`, `Concept-bayesflow-make-simulator`, `Concept-gru`;
  `needs-review`: `Code-experiments`, `Code-process-scripts`. `needs-revision` (I owe a
  rewrite): `Concept-flow-matching`.
- **One convention for `y` in all our Models** (Opher, 2026-10-12, after a reversal the
  same day): `y = x + ε` is the hand (the movement) and `e = y + p` is the error, as in
  decision 0005. The two-state work is back in that form.
  [Issue #34](https://github.com/opherdonchin/MotorAdpatationSBI/issues/34) and [PR #35](https://github.com/opherdonchin/MotorAdpatationSBI/pull/35), which changed the one-state
  Model the other way, are closed unmerged.
- Other open issues: resources in the wiki (#2), large-data storage policy (#3),
  BayesFlow/HSSM numpy conflict (#4), multicore PyMC sampling across platforms (#9),
  live test of the compaction hooks (#10), hooks for Copilot and Codex (#11),
  sequential training and fitting in BayesFlow and PyMC (#23).

## Debt

Skipped on purpose and still owed ([docs/process.md](process.md), *Debt*, proposed in
[PR #33](https://github.com/opherdonchin/MotorAdpatationSBI/pull/33)).

- [#31](https://github.com/opherdonchin/MotorAdpatationSBI/issues/31) (validation): the one-state posterior network has not been
  compared with an exact posterior; calibration for `B` was at the edge of detection.
- [#32](https://github.com/opherdonchin/MotorAdpatationSBI/issues/32) (validation): no exact reference is planned for the two-state
  posterior network.

## Next steps

1. **Two-state Model** ([issue #28](https://github.com/opherdonchin/MotorAdpatationSBI/issues/28)).
   - Settle [PR #29](https://github.com/opherdonchin/MotorAdpatationSBI/pull/29), then [PR #30](https://github.com/opherdonchin/MotorAdpatationSBI/pull/30).
   - Agree where the transforms between the six parameters and the six unbounded
     quantities live (two functions in `src/models/two_state.py` would be new helpers).
   - The posterior notebook, branch `sbi/two-state-posterior`: a working copy of the
     one-state notebook with the two-state Model. Done when feasibility, convergence
     and calibration each have a clear answer.
   - Afterwards, with both notebooks in front of us: what moves into `src/motor_sbi/`.
2. **Likelihood-ratio estimator for the one-state Model** (step C3c of #12): a concept
   page first, since the method is new to Opher; then a scope issue.
3. **A small hierarchical fit** with that estimator in HSSM or PyMC. Needs #4 (numpy
   conflict between BayesFlow and HSSM) and #9 (sampler setup) resolved first.
4. **Decide when to pay the validation debt** (#31, #32): before goal 2's results are
   relied on, or after the hierarchical fit shows the approach is worth validating.
5. Rewrite `Concept-flow-matching`, probably with a small notebook that trains a flow
   on a known normal posterior.
6. Smaller process items: test the compaction hooks (#10); hooks for Copilot and Codex
   (#11); whether the one-state code is renamed to `s_eta` and `s_epsilon`.
