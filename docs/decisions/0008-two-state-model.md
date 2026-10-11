# 0008 — Two-state Model: the published two-rate form, states ordered through positive differences

**Date:** 2026-10-11 · **Status:** Proposed

**Context:** the posterior network recovers the parameters of the one-state Model
([PR #24](https://github.com/opherdonchin/MotorAdpatationSBI/pull/24)). The next question
([issue #28](https://github.com/opherdonchin/MotorAdpatationSBI/issues/28)) is whether
the same approach works for a two-state Model, and that needs the Model and its Prior
fixed first. Opher's answers to the open points of the issue (2026-10-11): one planning
noise shared by the two states; the form the lab uses, which is the one of Hulst et al.
(2020); and the ordering of the two states expressed, as the lab does when fitting in
PyMC, through positive differences on the logit scale.

Source: Hulst, Mamlins, Frens, Chang, Göricke, Timmann and Donchin (2020), *Can we
improve slow learning in cerebellar patients?*, bioRxiv,
[doi:10.1101/2020.07.03.185959](https://doi.org/10.1101/2020.07.03.185959). The form
below was read from the paper's public model code,
[thomashulst/paper-slowlearning](https://github.com/thomashulst/paper-slowlearning)
(`modelStateSpace.txt`), not from the lab's private repository. It is the two-state
model of Smith, Ghazizadeh and Shadmehr (2006, PLoS Biology,
[doi:10.1371/journal.pbio.0040179](https://doi.org/10.1371/journal.pbio.0040179)) with
planning and execution noise.

**Decision:** the Model `two_state`, in the convention of
[0005](0005-one-state-model-published-form.md).

```math
x^f_{t+1} = A_f\, x^f_t - B_f\, v_t\, e_t + \eta^f_t, \qquad
x^s_{t+1} = A_s\, x^s_t - B_s\, v_t\, e_t + \eta^s_t
```

```math
y_t = x^f_t + x^s_t + \varepsilon_t, \qquad e_t = y_t + p_t
```

with $\eta^f_t$ and $\eta^s_t$ each $\mathcal N(0, \sigma_\eta^2)$ and
$\varepsilon_t \sim \mathcal N(0, \sigma_\varepsilon^2)$, all independent.

| Symbol | Meaning |
|---|---|
| $x^f_t$, $x^s_t$ | the fast and the slow part of the movement plan on trial $t$ (hidden) |
| $y_t$, $p_t$, $e_t$, $v_t$ | movement angle, perturbation, error and vision flag, as in 0005 |
| $A_f$, $A_s$ | retention of the fast and of the slow state |
| $B_f$, $B_s$ | adaptation rate of the fast and of the slow state |
| $\sigma_\eta$ | planning noise: standard deviation of the noise in each state |
| $\sigma_\varepsilon$ | execution noise: standard deviation of the noise in the movement |

- **One error, two learners.** Both states learn from the same error, and that error
  contains the execution noise, as in 0005. On a no-vision trial neither state learns;
  each decays by its own retention.
- **Shared planning noise.** Each state has its own noise draw on every trial, with the
  same standard deviation. The plan $x^f_t + x^s_t$ therefore picks up noise of variance
  $2\sigma_\eta^2$ per trial.
- **Fast and slow.** $A_f$ is below $A_s$ (the fast state forgets faster) and $B_f$ is
  above $B_s$ (it learns faster). Without this the two states could swap names and every
  posterior would have two mirror-image modes.
- **Parameters.**
  $\theta = (A_f, A_s, B_f, B_s, \sigma_\eta, \sigma_\varepsilon)$, in this order in
  code, named `A_fast`, `A_slow`, `B_fast`, `B_slow`, `sigma_eta`, `sigma_epsilon`.
- **Domains.** The four rates between 0 and 1, ordered as above; the two standard
  deviations positive.
- **First state.** $x^f_1$ and $x^s_1$ each $\mathcal N(0, \sigma_\eta^2)$, independent,
  following 0005. (The paper gives each a wide normal prior and estimates it.)
- **Units, Task and Schedules.** As in 0005: units of the perturbation size; the Task
  and the Schedule Design of the one-state Model, unchanged.

**Prior.** Each part is normal on an unbounded scale. The fast state's rates are drawn
on the logit scale, and each slow rate is the fast one moved by a positive difference,
also on the logit scale:

```math
\mathrm{logit}(A_s) = \mathrm{logit}(A_f) + d_A, \qquad
\mathrm{logit}(B_s) = \mathrm{logit}(B_f) - d_B, \qquad d_A, d_B > 0
```

| Quantity | Range (95%) | Prior | Median |
|---|---|---|---|
| $A_f$ | 0.30 to 0.95 | $\mathrm{logit}(A_f) \sim \mathcal N(1.05, 0.97)$ | 0.74 |
| $d_A$ | 1.5 to 7 | $\log d_A \sim \mathcal N(1.18, 0.39)$ | 3.25 |
| $B_f$ | 0.05 to 0.60 | $\mathrm{logit}(B_f) \sim \mathcal N(-1.27, 0.85)$ | 0.22 |
| $d_B$ | 0.7 to 5 | $\log d_B \sim \mathcal N(0.63, 0.50)$ | 1.88 |
| $\sigma_\varepsilon$ | 1/15 to 1/3 | $\log \sigma_\varepsilon \sim \mathcal N(-1.90, 0.41)$ | 0.149 |
| $\sigma_\eta / \sigma_\varepsilon$ | 1/15 to 1/5 | $\log(\sigma_\eta/\sigma_\varepsilon) \sim \mathcal N(-2.16, 0.28)$ | 0.115 |

The six normal draws are independent. The two noise rows are those of 0005. The four
rate rows are new and are **my proposal, for Opher to correct**: I chose them to
surround values reported for two-state fits (Smith et al. 2006: $A_f = 0.59$,
$A_s = 0.992$, $B_f = 0.21$, $B_s = 0.02$), not from the lab's priors, which I have not
seen.

What these imply for the quantities that have no row of their own (one-off calculation,
2026-10-11, one million draws):

| Quantity | 2.5% | Median | 97.5% |
|---|---|---|---|
| $A_s$ | 0.840 | 0.988 | 0.9998 |
| $B_s$ | 0.001 | 0.037 | 0.26 |
| fast time constant, $-1/\log A_f$ (trials) | 0.8 | 3.3 | 20 |
| slow time constant, $-1/\log A_s$ (trials) | 5.7 | 81 | 4,600 |
| adaptation reached under a constant perturbation (fraction of it) | 0.23 | 0.81 | 0.996 |
| share of that adaptation held by the slow state | 0.10 | 0.77 | 0.99 |

- **Stability.** The Model is stable when
  $B_f/(1+A_f) + B_s/(1+A_s)$ is below 1; otherwise the movement swings from side to
  side with growing size. Under this Prior that happens in about 13 draws per million.
  The Prior is defined as truncated to the stable region: the Prior Sampler draws again
  when a draw falls outside it.

**Why:**

- *The published form* for the same reasons as in 0005: the symbols and sign are those
  of the paper and of the lab's code, and the lab's data can be used without conversion.
  It also contains the one-state Model as a special case in distribution ($B_f$ and the
  fast state's noise going to zero), which gives a Check.
- *Shared planning noise* (Opher): it is the published form, and it is the simpler
  start, with six parameters instead of seven.
- *Positive differences* (Opher): in the lab's experience this was the best
  parameterization for fitting in PyMC, and it makes priors easy to state: one for the
  fast rate, one for how far the slow rate is from it. The ordering holds by
  construction and nothing is truncated or rejected to get it. The paper orders the
  states by truncating the slow rate's prior at the fast rate; a hierarchical version
  would be awkward with that, and ours is meant to become hierarchical.
- *Differences on the logit scale, with log-normal priors:* the rates live on the logit
  scale already, so a difference there keeps both rates between 0 and 1 whatever its
  size; a log-normal keeps the difference positive and lets its 95% range be stated
  directly, like every other row.

*Alternatives:* a planning noise for each state (seven parameters; left until the
shared one is understood); ordering by truncation, as in the paper (see above); no
ordering, with the labels sorted out afterwards (two modes in every posterior, which a
posterior network learns poorly); a free first state for each state, as in the paper
(two more parameters that one Sitting says little about); leaving unstable draws in the
Prior (a handful of training Sittings with values of any size).

**Consequences:**

- Six parameters are estimated from the same data that carried four. The slow
  retention and the split of learning between the states are known to trade off against
  each other, so weaker contraction for some parameters is expected and is something
  [issue #28](https://github.com/opherdonchin/MotorAdpatationSBI/issues/28) measures.
- The posterior network will work with the six unbounded quantities of the Prior table
  (the two logits, the two log differences and the two logs for the noise), and results
  are reported for the six parameters. The transforms between the two are defined once,
  in `src/models/two_state.py`.
- The slow time constant reaches thousands of trials at the top of the Prior, longer
  than any Sitting. Such values cannot be told apart from perfect retention; the Check
  by Sitting length will show where that starts.
- The Prior Sampler redraws unstable draws. This is the first Prior in the repo that is
  not a product of independent parts, which matters when an exact density of the Prior
  is needed (stage 2 of
  [issue #12](https://github.com/opherdonchin/MotorAdpatationSBI/issues/12), for this
  Model later).
