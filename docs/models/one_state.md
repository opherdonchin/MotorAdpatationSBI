# One-state Model

The one-state Model of visuomotor adaptation of van der Vliet et al. (2018, eNeuro,
[doi:10.1523/ENEURO.0170-18.2018](https://doi.org/10.1523/ENEURO.0170-18.2018)),
equations 1 to 4, with a vision flag. Why this form:
[decision 0005](../decisions/0005-one-state-model-published-form.md). Terms such as
Sitting, Schedule and Block: [glossary](../glossary.md).

## The Model

For Trials $t = 1, \dots, T$ of one Sitting:

```math
x_1 \sim \mathcal N(0, \sigma_\eta^2)
```

```math
y_t = x_t + \varepsilon_t, \qquad e_t = y_t + p_t, \qquad
x_{t+1} = A\, x_t - B\, v_t\, e_t + \eta_t
```

with $\varepsilon_t \sim \mathcal N(0, \sigma_\varepsilon^2)$ and
$\eta_t \sim \mathcal N(0, \sigma_\eta^2)$, all independent. Everything is in units of
the perturbation size, so $p_t \in \lbrace 0, +1, -1 \rbrace$.

| Symbol | Meaning | Domain |
|---|---|---|
| $x_t$ | aiming angle: the movement plan (hidden) | |
| $y_t$ | movement angle: what the subject did (recorded) | |
| $p_t$ | perturbation applied to the cursor (part of the Condition) | $0$, $+1$ or $-1$ |
| $v_t$ | vision flag: 1 if the cursor is shown, 0 if not (part of the Condition) | $0$ or $1$ |
| $e_t$ | error: where the cursor went, relative to the target | |
| $A$ | retention: fraction of the plan kept from one Trial to the next | between 0 and 1 |
| $B$ | adaptation rate: fraction of the error corrected | between 0 and 1 |
| $\sigma_\eta$ | planning noise: standard deviation of the noise in the plan | positive |
| $\sigma_\varepsilon$ | execution noise: standard deviation of the noise in the movement | positive |

The Schedule of a Sitting is $p_t$ and $v_t$ on every Trial.

The execution noise $\varepsilon_t$ is part of the movement, and so of the error, so it is
fed back into the next plan. On a no-vision Trial ($v_t = 0$) there is no error to learn
from: the plan decays by $A$ and picks up planning noise.

**Code.** [src/models/one_state.py](../../src/models/one_state.py) names the Task the Model
is written for, `TASK`, the visuomotor adaptation Task of
[src/designs/visuomotor_adaptation_task.py](../../src/designs/visuomotor_adaptation_task.py)
(its Schedules hold `p` and `v`, its Sittings add `y`), and the Model's `PARAMETERS`
(`A`, `B`, `sigma_eta`, `sigma_epsilon`, the order of $\theta$). The Simulator,
`simulate_sitting(rng, theta, schedule)`, takes a Schedule as a dict with exactly the keys
`p` and `v`, and returns the Observations (`y`) and, separately, the Ground Truth (the
parameter values and the plans `x`). Where each piece lives:
[decision 0006](../decisions/0006-models-tasks-and-designs.md).

## Derived properties

Checked against the Simulator in
[notebooks/working/one_state_simulator.ipynb](../../notebooks/working/one_state_simulator.ipynb).

**Without noise,** with vision and a constant perturbation $p$, the movement approaches a
fixed point geometrically:

```math
y_{t+1} - y^* = (A - B)\,(y_t - y^*), \qquad y^* = -\frac{B\, p}{1 - A + B}
```

Without vision it only decays: $y_{t+1} = A\, y_t$. (`#[check-noise-free]`: largest
difference from the Simulator 6e-12.)

**With noise,** under a constant perturbation the movements settle into a stationary
fluctuation around the fixed point. With vision the plan follows
$x_{t+1} - x^* = (A - B)(x_t - x^*) - B\,\varepsilon_t + \eta_t$, so its variance is
$V_x = (\sigma_\eta^2 + B^2 \sigma_\varepsilon^2) / (1 - (A - B)^2)$ and

```math
\sigma_y^2 = \sigma_\varepsilon^2 + V_x, \qquad
R(1) = \frac{(A - B)\, V_x - B\, \sigma_\varepsilon^2}{\sigma_y^2}
```

where $R(1)$ is the correlation between successive movements. The $-B\sigma_\varepsilon^2$
term is the execution noise of one Trial being corrected on the next. Without vision
($B$ drops out):

```math
\sigma_y^2 = \sigma_\varepsilon^2 + \frac{\sigma_\eta^2}{1 - A^2}, \qquad
R(1) = \frac{A\, \sigma_\eta^2 / (1 - A^2)}{\sigma_y^2}
```

These are equations 9, 11 and 12 of the paper with the geometric sums added up. The
paper's equation 10, for $R(1)$ with vision, is printed differently: $+B\sigma_\varepsilon^2$
in the numerator, and $A^k (A - B)^k$ in place of $(A - B)^{2k}$ in the denominator. The
version above is derived here and agrees with simulation; the printed one does not
(`#[check-stationary]`: all 16 z-scores below 1.6 for the derived formulas).

## Likelihood

Not yet written. The Model is linear and Gaussian, so a Kalman filter gives the exact
likelihood of a Sitting; it comes in stage 2 of issue [#12](https://github.com/opherdonchin/MotorAdpatationSBI/issues/12)
(validation).

## Experiments, Inference Engines and Analyses

### Prior and Schedule Design for the Simulated Experiments of issue #12

The Simulated Experiments that BayesFlow will be trained and tested on (scope
issue [#12](https://github.com/opherdonchin/MotorAdpatationSBI/issues/12)) draw each
Sitting's parameter values from this Prior and its Schedule from this Schedule Design,
both from [decision 0005](../decisions/0005-one-state-model-published-form.md). Checks:
[notebooks/working/one_state_priors.ipynb](../../notebooks/working/one_state_priors.ipynb).

**Prior.** Each part is normal on an unbounded scale, with the stated range as its
central 95% interval; the constants are computed from the ranges in
`one_state_priors.ipynb#[config]`. Prior Sampler: `sample_prior(rng, size, prior)`, with the
Prior's constants in one dict.

| Quantity | Range (95%) | Prior |
|---|---|---|
| $A$ | 0.75 to 0.999 | $\mathrm{logit}(A) \sim \mathcal N(4.00, 1.48)$ |
| $B$ | 0.01 to 0.5 | $\mathrm{logit}(B) \sim \mathcal N(-2.30, 1.17)$ |
| $\sigma_\varepsilon$ | 1/15 to 1/3 | $\log \sigma_\varepsilon \sim \mathcal N(-1.90, 0.41)$ |
| $\sigma_\eta / \sigma_\varepsilon$ | 1/15 to 1/5 | $\log(\sigma_\eta/\sigma_\varepsilon) \sim \mathcal N(-2.16, 0.28)$ |

The second number of each normal is its standard deviation. $\sigma_\eta$ is the
execution noise times the ratio.

**Schedule Design.** There are four Trial Types: baseline ($p = 0$, $v = 1$), perturbation
$+1$ or $-1$ ($v = 1$), and no vision ($v = 0$, $p$ set to 0). A Sitting is a sequence of
Blocks, each a run of Trials of one Trial Type. Both belong to the Task, not the Model,
and live in
[src/designs/visuomotor_adaptation_experiment.py](../../src/designs/visuomotor_adaptation_experiment.py):
the Trial Types in `TRIAL_TYPES`, and the Schedule Generator
`sample_schedule(rng, schedule_design)`, which returns the Schedule as a dict of $p_t$ and
$v_t$.

- 5 to 16 Blocks, equally likely.
- Block lengths independent, $\log L \sim \mathcal N(3.91, 0.82)$ (central 95% interval
  10 to 250 Trials, median 50), rounded to whole Trials.
- The first Block is a baseline. Each Sitting draws its proportions of the four Trial
  Types from a symmetric Dirichlet with concentration 3; every later Block's Trial Type
  is drawn independently with those proportions. Neighbouring Blocks of the same Trial
  Type make one longer Block.

**Results.** Prior quantiles match the stated ranges within sampling error. Sittings have
about 230 to 1,440 Trials (central 95%), median about 700. With few Blocks, many
Sittings lack a Trial Type: about 16% have no no-vision Block, about 17% lack each
perturbation, and 2.4% have no perturbation at all.

### Simulated Experiment `one_state_random_blocks_test`

300 Sittings for testing Inference Engines: 30 Schedules from the Schedule Design above
(270 to 1,771 Trials), with 10 Sittings on each, every Sitting with its own parameter
values from the Prior above. Simulated and saved by
[notebooks/one_state_posterior.ipynb](../../notebooks/one_state_posterior.ipynb)
(`#[simulate-test]`) in `data/simulated/one_state_random_blocks_test/`.

### Inference Engine `posterior_random_blocks`

**What it is.** A BayesFlow posterior network for the four parameters given one Sitting
at its full length: a `TimeSeriesNetwork` summary network (12 summary numbers) and a
flow-matching inference network
([decision 0007](../decisions/0007-summary-network-for-sittings.md)). Trained on 960,000
Sittings simulated as needed from the Prior and Schedule Design above, in batches of 32
Sittings that share one Schedule, so nothing is padded.

**Question.** Can a network trained once on simulated Sittings give a trustworthy
posterior for a new Sitting (step C3b of issue
[#12](https://github.com/opherdonchin/MotorAdpatationSBI/issues/12))?

**Notebook and folder.**
[notebooks/one_state_posterior.ipynb](../../notebooks/one_state_posterior.ipynb);
`outputs/one_state/engines/posterior_random_blocks/`.

**Result** (run of 2026-10-10, on `one_state_random_blocks_test`). Training took 1.2
hours and had nearly levelled off. Recovery is good for all four parameters and
calibration passes for all four, narrowly for $B$ (its posterior sits a little low and
is a little wide).

| | $A$ | $B$ | $\sigma_\eta$ | $\sigma_\varepsilon$ |
|---|---|---|---|---|
| Correlation of posterior median with truth | 0.94 | 0.99 | 0.89 | 1.00 |
| Posterior contraction | 0.997 | 0.993 | 0.84 | 0.994 |
| Calibration error | 0.01 | 0.04 | 0.02 | 0.02 |
| Log Gamma (below 0: calibration rejected at 5%) | 1.0 | 1.5 | 2.4 | 1.9 |
| Mean offset of the posterior, in posterior standard deviations | 0.04 | -0.08 | -0.05 | -0.05 |

An earlier run with the same seed ended with $B$ just outside the calibration band (Log
Gamma -3.2); training on a graphics card is not reproducible bit for bit, and $B$ is at
the edge of what 300 test Sittings can detect. Calibration does not clearly differ
between shorter and longer Sittings. Not yet compared with an exact posterior; that is
stage 2 of issue #12.
