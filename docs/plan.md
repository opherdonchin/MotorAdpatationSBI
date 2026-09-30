# Plan

Current goals and next steps. Rewritten in place; see git history for earlier versions.

## Current goals

1. **Quick win: BayesFlow parameter recovery on a one-state model.** A one-state
   motor-adaptation state-space model with state and output noise,

   $$x_{t+1} = A\,x_t + B\,(p_t - y_t) + \eta_t,\qquad y_t = x_t + \varepsilon_t,$$

   with $\eta_t \sim \mathcal N(0,\sigma_x^2)$ and $\varepsilon_t \sim \mathcal N(0,\sigma_y^2)$,
   on a fixed perturbation schedule. BayesFlow learns a likelihood-to-evidence ratio
   (NRE); success is agreement with the exact Kalman likelihood and good parameter
   recovery and calibration.
2. **Next quick win:** the same learned likelihood used inside HSSM for a small
   hierarchical fit.
3. **Side project:** a working process that keeps the human fully in the loop and
   produces shareable documentation as a byproduct.

## Current state

- Agent instructions: [AGENTS.md](../AGENTS.md) (PR #1).
- Open issues: background resources (#2), large-data storage policy (#3).

## Next steps

1. Environment PR: pixi, Python 3.12, BayesFlow, Keras (JAX backend), PyMC; register
   `simulators/` as importable alongside `src/motor_sbi/`.
2. Human-in-the-loop PR: `docs/process.md`, first journal entry and decision records
   (pixi, model choice), project skills `new-experiment`, `explain-pr`, `journal`.
3. One-state study: agree on correctness checks, then an `explore_` notebook in
   `notebooks/` with outputs under `analyses/sim/one_state/`.
