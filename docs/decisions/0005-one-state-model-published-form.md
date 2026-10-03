# 0005 — One-state model in its published form, with no-vision trials

**Date:** 2026-10-02 · **Status:** Accepted

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

**Schedules.** Each simulated sitting has its own schedule, made of blocks. A block is
one of four kinds: baseline ($p_t = 0$), perturbation $+1$, perturbation $-1$, or no
vision ($v_t = 0$; the cursor is not shown, so $p_t$ has no effect and is set to 0).
Vision is on ($v_t = 1$) in every block that is not a no-vision block.

- *Number of blocks:* 8 to 60, equally likely.
- *Block lengths:* independent, log-normal with central 95% interval 10 to 50 trials
  ($\log L \sim \mathcal N(3.11, 0.41)$, median 22), rounded to whole trials. With 8 to 60
  blocks, sittings are about 210 to 1,480 trials long (central 95%), median about 830.
- *Kinds:* the first block is a baseline block. Each sitting draws its own proportions of
  the four kinds from a symmetric Dirichlet distribution with concentration 3 for each
  kind, and every later block's kind is drawn independently with those proportions. Two
  neighbouring blocks of the same kind make, in effect, one longer block.

With concentration 3, one kind can take up to about 0.6 of a sitting's blocks (the
largest proportion in a sitting is below 0.60 in 97.5% of sittings), and the typical
smallest proportion is 0.12. Each single proportion is below 0.1 in 9% of sittings and
above 0.7 in 0.06%. Concentration 2 would let one kind reach about 0.7, at the cost of
more sittings in which some kind is nearly absent. (One-off calculation, 2026-10-03.)

**Why:** Using the published form means the model, the symbols and the sign are the
ones in the paper and in the lab's code, and the lab's data (movement angles,
perturbations, vision flags) can be used without conversion. The vision flag is needed
for those data in any case, and no-vision trials are what let the two noises be told
apart: without correction the planning noise accumulates from trial to trial and shows
up as correlation between successive movements, while execution noise does not.

*Alternatives:* keeping the convention of 0002 (no change to code already written, but a
private dialect of a published model); a vision flag in the model with all-vision
simulated sittings (the model would be ready for real data, but the simulations would
not exercise it); no-vision trials scattered one by one instead of in blocks (rejected:
no vision is a condition the experimenter sets for a stretch of trials, like a
perturbation); proportions of block kinds closer to real experiments, where baseline and
no-vision blocks together are about 20% and the two perturbations the rest (left for
later: for training, a prior that covers every mix is more useful); a fixed rule that
neighbouring blocks must differ (it caps the share of any one kind at one half).

**Consequences:**

- 0002 is superseded. What it says about the exact likelihood still holds in substance
  (the model is linear and Gaussian, so a Kalman filter gives the likelihood of a
  sitting); that math is written out again, in this convention, when the filter is built.
- The code on the branch `sim/one-state-kalman` is in the convention of 0002 and has no
  vision flag. Whatever is taken from it is converted.
- How well the two noises are identified is no longer assumed, in either direction. The
  paper separated them with 900 trials, 275 of them without vision; sittings here cover
  that range (about 210 to 1,480 trials). Identification is measured for these
  schedules, not taken from the paper.
- Sittings of up to about 1,500 trials make each simulation, and each input to the
  network, about five times longer than in the first attempt.
