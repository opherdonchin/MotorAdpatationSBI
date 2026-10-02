# 0005 — One-state model in its published form, with no-vision trials

**Date:** 2026-10-02 · **Status:** Proposed

**Context:** [0002](0002-one-state-model.md) chose a one-state model with state and
output noise for the first quick win. The review of PR #13 showed three things. The
model is the one of van der Vliet et al. (2018, eNeuro,
[doi:10.1523/ENEURO.0170-18.2018](https://doi.org/10.1523/ENEURO.0170-18.2018)), written
in a different convention. The lab already has code for it (`state-space-models`), which
also handles trials without visual feedback. And the simulated sittings of 0002 had no
such trials, which left the ratio of the two noises almost unidentified.

**Decision:** Use the published form, with a vision flag.

```math
x_{t+1} = A\, x_t - B\, v_t\, e_t + \eta_t, \qquad y_t = x_t + \varepsilon_t, \qquad e_t = y_t + p_t
```

with $\eta_t \sim \mathcal N(0, \sigma_\eta^2)$ and
$\varepsilon_t \sim \mathcal N(0, \sigma_\varepsilon^2)$, all independent.

| Symbol | Meaning |
|---|---|
| $x_t$ | aiming angle on trial $t$: the movement plan (hidden) |
| $y_t$ | movement angle: what the subject actually did (observed) |
| $p_t$ | perturbation applied to the cursor |
| $e_t$ | error: where the cursor went relative to the target |
| $v_t$ | vision flag: 1 if the cursor was shown, 0 if not |
| $A$ | retention: the fraction of the plan kept from one trial to the next |
| $B$ | adaptation rate: the fraction of the error corrected |
| $\sigma_\eta$ | planning noise: standard deviation of the noise in the plan |
| $\sigma_\varepsilon$ | execution noise: standard deviation of the noise in the movement |

- **Sign.** The error is $y_t + p_t$ and it is subtracted, so a learner compensates by
  moving to $y = -p$. (In 0002 the error was $p_t - y_t$ and a learner moved to $+p$.)
- **Where the execution noise goes.** $\varepsilon_t$ is part of $y_t$, and $y_t$ is
  part of the error, so the execution noise of a trial is fed back into the next plan.
- **No-vision trials.** When $v_t = 0$ the subject sees no error and does not learn from
  that trial: the plan only decays by $A$ and picks up planning noise.
- **Parameters.** $\theta = (A, B, \sigma_\eta, \sigma_\varepsilon)$, in this order in
  code, named `A`, `B`, `sigma_eta`, `sigma_epsilon`.
- **Domains.** $A$ and $B$ between 0 and 1; $\sigma_\eta$ and $\sigma_\varepsilon$ positive.
- **First state.** $x_1 \sim \mathcal N(0, \sigma_\eta^2)$, as in 0002. (The lab code
  instead has a free first state and first-state variance.)
- **Units.** Everything is in units of the perturbation size, so
  $p_t \in \lbrace 0, +1, -1 \rbrace$, as in 0002.

**Priors,** unchanged from 0002 apart from the names. Each is normal on an unbounded
scale, with the stated range as its central 95% interval; the second number of each
normal is its standard deviation.

| Quantity | Range (95%) | Prior | Median |
|---|---|---|---|
| $A$ | 0.75 to 0.999 | $\mathrm{logit}(A) \sim \mathcal N(4.00, 1.48)$ | 0.982 |
| $B$ | 0.01 to 0.5 | $\mathrm{logit}(B) \sim \mathcal N(-2.30, 1.17)$ | 0.091 |
| $\sigma_\varepsilon$ | 1/15 to 1/3 | $\log \sigma_\varepsilon \sim \mathcal N(-1.90, 0.41)$ | 0.149 |
| $\sigma_\eta / \sigma_\varepsilon$ | 1/15 to 1/5 | $\log(\sigma_\eta/\sigma_\varepsilon) \sim \mathcal N(-2.16, 0.28)$ | 0.115 |

The planning noise has no prior of its own; it is the execution noise times the ratio.

**Schedules.** Each simulated sitting has its own schedule.

- *Perturbation,* unchanged from 0002: 3 to 10 blocks, equally likely; $p_t$ constant
  within a block; the first block is a baseline ($p_t = 0$); at every block boundary
  $p_t$ changes to one of the other two values, equally likely; block lengths log-normal
  with central 95% interval 10 to 50 trials, rounded to whole trials.
- *Vision,* new, **a proposal for Opher to edit:** each sitting draws a fraction of
  no-vision trials uniformly between 0 and 0.5, and each trial is then a no-vision trial
  with that probability, independently of the others. This covers both parts of the
  paper's experiment (half of the baseline trials without vision, one in nine afterwards)
  and all-vision sittings.

**Why:** Using the published form means the model, the symbols and the sign are the
ones in the paper and in the lab's code, and the lab's data (movement angles,
perturbations, vision flags) can be used without conversion. The vision flag is needed
for those data in any case, and no-vision trials are what let the two noises be told
apart: without correction the planning noise accumulates from trial to trial and shows
up as correlation between successive movements, while execution noise does not.

*Alternatives:* keeping the convention of 0002 (no change to code already written, but a
private dialect of a published model); a vision flag in the model with all-vision
simulated sittings (the model would be ready for real data, but the simulations would
not exercise it); no-vision trials in whole blocks instead of scattered (closer to the
paper's 30-trial no-vision run; scattered was chosen as the simpler rule to state).

**Consequences:**

- 0002 is superseded. What it says about the exact likelihood still holds in substance
  (the model is linear and Gaussian, so a Kalman filter gives the likelihood of a
  sitting); that math is written out again, in this convention, when the filter is built.
- The code on the branch `sim/one-state-kalman` is in the convention of 0002 and has no
  vision flag. Whatever is taken from it is converted.
- How well the two noises are identified is no longer assumed, in either direction. The
  paper separated them with 900 trials, 275 of them without vision. Sittings here are
  about 55 to 280 trials. Identification is measured for these schedules, and the length
  of the sittings is revisited if it is not good enough.
