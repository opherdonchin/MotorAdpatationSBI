# Two-state Model

The two-state Model of visuomotor adaptation in the form of Hulst et al. (2020, bioRxiv,
[doi:10.1101/2020.07.03.185959](https://doi.org/10.1101/2020.07.03.185959)): the model
of Smith, Ghazizadeh and Shadmehr (2006, PLoS Biology,
[doi:10.1371/journal.pbio.0040179](https://doi.org/10.1371/journal.pbio.0040179)) with
planning and execution noise and a vision flag. Why this form:
[decision 0008](../decisions/0008-two-state-model.md). Terms such as Sitting, Schedule
and Block: [glossary](../glossary.md). It is written to be read next to the
[one-state Model](one_state.md), whose Task, units and Schedule Design it shares.

## The Model

For Trials $t = 1, \dots, T$ of one Sitting:

```math
x^f_1,\ x^s_1 \sim \mathcal N(0, \sigma_\eta^2)
```

```math
y_t = x^f_t + x^s_t + \varepsilon_t, \qquad e_t = y_t + p_t
```

```math
x^f_{t+1} = A_f\, x^f_t - B_f\, v_t\, e_t + \eta^f_t, \qquad
x^s_{t+1} = A_s\, x^s_t - B_s\, v_t\, e_t + \eta^s_t
```

with $\varepsilon_t \sim \mathcal N(0, \sigma_\varepsilon^2)$ and $\eta^f_t$, $\eta^s_t$
each $\mathcal N(0, \sigma_\eta^2)$, all independent. Everything is in units of the
perturbation size, so $p_t \in \lbrace 0, +1, -1 \rbrace$.

| Symbol | Meaning | Domain |
|---|---|---|
| $x^f_t$, $x^s_t$ | the fast and the slow part of the movement plan (hidden) | |
| $y_t$ | movement angle: what the subject did (recorded) | |
| $p_t$ | perturbation applied to the cursor (part of the Condition) | $0$, $+1$ or $-1$ |
| $v_t$ | vision flag: 1 if the cursor is shown, 0 if not (part of the Condition) | $0$ or $1$ |
| $e_t$ | error: where the cursor went, relative to the target | |
| $A_f$, $A_s$ | retention of the fast and of the slow state | between 0 and 1, $A_f$ below $A_s$ |
| $B_f$, $B_s$ | adaptation rate of the fast and of the slow state | between 0 and 1, $B_f$ above $B_s$ |
| $\sigma_\eta$ | planning noise: standard deviation of the noise in each state | positive |
| $\sigma_\varepsilon$ | execution noise: standard deviation of the noise in the movement | positive |

Both states learn from the same error, which contains the execution noise. On a
no-vision Trial ($v_t = 0$) neither learns: each decays by its own retention and picks
up planning noise. The planning noise has one standard deviation, and each state has its
own draw, so the plan $x^f_t + x^s_t$ picks up variance $2\sigma_\eta^2$ per Trial.

**Code.** [src/models/two_state.py](../../src/models/two_state.py) provides the names
every Model provides ([decision 0006](../decisions/0006-models-tasks-and-designs.md)):
`TASK`, the visuomotor adaptation Task; `PARAMETERS` (`Af`, `As`, `Bf`, `Bs`, `s_eta`,
`s_epsilon`, the order of $\theta$); the Simulator,
`simulate_sitting(rng, theta, schedule)`, which returns the Observations (`y`) and,
separately, the Ground Truth (the parameter values and the states `x_fast` and
`x_slow`); and the Prior Sampler, `sample_prior(rng, size, prior)`.

## Derived properties

Checked against the Simulator in
[notebooks/working/two_state_simulator.ipynb](../../notebooks/working/two_state_simulator.ipynb)
(run of 2026-10-12).

Write $s_t = (x^f_t, x^s_t)$, $b = (B_f, B_s)$ and $\mathbf 1 = (1, 1)$.

**Without noise,** with vision and a constant perturbation $p$:

```math
s_{t+1} = S\, s_t - b\, p, \qquad
S = \begin{pmatrix} A_f - B_f & -B_f \\ -B_s & A_s - B_s \end{pmatrix}, \qquad
s_t = s^* + S^{t}\,(s_0 - s^*), \qquad s^* = -(I - S)^{-1} b\, p
```

Without vision each state decays by its own retention. (`#[check-noise-free]`: largest
difference from the Simulator 1e-11.) The movement settles at

```math
y^* = -p\, \frac{K}{1 + K}, \qquad K = \frac{B_f}{1 - A_f} + \frac{B_s}{1 - A_s}
```

and the slow state holds the share $\big(B_s/(1-A_s)\big)/K$ of it.

**Stability.** The Model is stable when $B_f/(1+A_f) + B_s/(1+A_s)$ is below 1.
Otherwise the movement swings from side to side with growing size.

**Spontaneous recovery.** After a long adaptation and a short reversal, the movement is
near zero because the fast state has been pushed the other way while the slow state
still holds the adaptation. Without vision the fast state decays first and the movement
returns toward the first adaptation. With the rates of Smith et al. (2006), 200 Trials
of adaptation and 12 of reversal: movement $+0.14$ on the first no-vision Trial and
$-0.29$ nine Trials later (`#[check-spontaneous-recovery]`).

**With noise,** under a constant perturbation with vision, the covariance $P$ of the two
states solves

```math
P = S\, P\, S^\top + \sigma_\varepsilon^2\, b\, b^\top + \sigma_\eta^2\, I
```

and the movements have

```math
\sigma_y^2 = \mathbf 1^\top P\, \mathbf 1 + \sigma_\varepsilon^2, \qquad
R(1) = \frac{\mathbf 1^\top S\, P\, \mathbf 1 - \sigma_\varepsilon^2\, \mathbf 1^\top b}{\sigma_y^2}
```

where $R(1)$ is the correlation between successive movements. Without vision the same
holds with $b = 0$ and $S$ the diagonal matrix of the retentions. (`#[check-stationary]`:
four parameter sets, with and without vision; all 16 z-scores at most 2.0 in size.)

**The link to the one-state Model.** With a shared planning noise neither state can be
switched off, so the one-state Model is not a special case. When $A_f = A_s = A$, the
plan $x^f_t + x^s_t$ follows the one-state Model with adaptation rate $B_f + B_s$ and
planning noise $\sqrt 2\, \sigma_\eta$. (`#[check-equal-retention]`: noise-free
movements of the two Simulators differ by at most 1.4e-11; with noise, the steady-state
values above equal the one-state formulas' to four decimals.)

## Likelihood

Not written. The Model is linear and Gaussian, so a Kalman filter with a two-part state
gives the exact likelihood of a Sitting. It is out of scope of
[issue #28](https://github.com/opherdonchin/MotorAdpatationSBI/issues/28).

## Experiments, Inference Engines and Analyses

### Prior and Schedule Design for the Simulated Experiments of issue #28

**Prior** ([decision 0008](../decisions/0008-two-state-model.md), which shows the three
steps). It starts from a central 95% range for each rate, as a number between 0 and 1:

| Rate | Range (95%) |
|---|---|
| $A_f$ | 0.70 to 0.90 |
| $A_s$ | 0.95 to 0.999 |
| $B_f$ | 0.10 to 0.35 |
| $B_s$ | 0.001 to 0.05 |

Each range becomes a normal on the logit scale. The slow rates are then expressed
through positive differences on that scale,
$d_A = \mathrm{logit}(A_s) - \mathrm{logit}(A_f)$ and
$d_B = \mathrm{logit}(B_f) - \mathrm{logit}(B_s)$, each log-normal with the mean and
variance that give the slow rate's logit its mean and variance. The Prior Sampler draws
six independent normals; the constants are computed from the ranges in
`two_state_simulator.ipynb#[config]`.

| Quantity | Prior |
|---|---|
| $A_f$ | $\mathrm{logit}(A_f) \sim \mathcal N(1.52, 0.34)$ |
| $d_A$ | $\log d_A \sim \mathcal N(1.19, 0.27)$ |
| $B_f$ | $\mathrm{logit}(B_f) \sim \mathcal N(-1.41, 0.40)$ |
| $d_B$ | $\log d_B \sim \mathcal N(1.22, 0.26)$ |
| $\sigma_\varepsilon$ | $\log \sigma_\varepsilon \sim \mathcal N(-1.90, 0.41)$ (range 1/15 to 1/3) |
| $\sigma_\eta / \sigma_\varepsilon$ | $\log(\sigma_\eta/\sigma_\varepsilon) \sim \mathcal N(-2.16, 0.28)$ (range 1/15 to 1/5) |

The second number of each normal is its standard deviation.

**Schedule Design.** That of the one-state Model, unchanged:
[one_state.md](one_state.md), *Schedule Design*.

**Results** (`two_state_simulator.ipynb`, run of 2026-10-12, a million draws). $A_f$,
$B_f$ and the noise quantities have their stated ranges within sampling error. The slow
rates, whose translation is approximate, come out close to theirs. What the Prior gives
(2.5%, median, 97.5%):

| Quantity | 2.5% | Median | 97.5% |
|---|---|---|---|
| $A_s$ (stated 0.95 to 0.999) | 0.963 | 0.992 | 0.9993 |
| $B_s$ (stated 0.001 to 0.05) | 0.0008 | 0.008 | 0.038 |
| $\sigma_\eta$ | 0.007 | 0.017 | 0.046 |
| fast time constant, $-1/\log A_f$ (Trials) | 2.8 | 5.1 | 9.5 |
| slow time constant, $-1/\log A_s$ (Trials) | 27 | 124 | 1,400 |
| slow time constant divided by fast | 6 | 24 | 250 |
| adaptation reached under a constant perturbation (fraction of it) | 0.41 | 0.69 | 0.95 |
| the slow state's share of it | 0.06 | 0.48 | 0.93 |

The states stay apart: in a million draws the slow time constant was never less than
2.4 times the fast one, and $B_s$ never above half of $B_f$ (`#[states-apart]`). No draw
is near instability (the stability quantity never exceeds 0.38).

In simulated Sittings (`#[generated-sittings]`) the slow state wanders visibly when its
retention is near 1: it receives the same planning noise as the fast state and forgets
little of it (standard deviation $\sigma_\eta/\sqrt{1-A_s^2}$).
