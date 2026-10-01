# one_state

**Question.** Can BayesFlow learn the likelihood of the one-state motor-adaptation model
([decision 0002](../../../docs/decisions/0002-one-state-model.md)) well enough to recover
its parameters, judged against the exact Kalman likelihood?

**Scope.** [#12](https://github.com/opherdonchin/MotorAdpatationSBI/issues/12), which
lists the agreed correctness checks (1 to 4 for the exact reference, 5 to 8 for the
learned likelihood).

**Notebook.** [notebooks/explore_one_state.ipynb](../../../notebooks/explore_one_state.ipynb).

**Outputs** (gitignored; each records the root seed and git commit that produced it):

| File | Produced by | Contents |
|---|---|---|
| `exact_sbc.npz` | `explore_one_state.ipynb#[sbc-run]` | True parameters, sitting lengths, posterior draws and sampler diagnostics for the SBC sittings fitted with the exact likelihood |
