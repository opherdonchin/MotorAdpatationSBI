# One-state model

The one-state model of visuomotor adaptation of van der Vliet et al. (2018, eNeuro,
[doi:10.1523/ENEURO.0170-18.2018](https://doi.org/10.1523/ENEURO.0170-18.2018)),
equations 1 to 4, with a vision flag. Why this form:
[decision 0005](../decisions/0005-one-state-model-published-form.md).

Code: `simulate_sitting` in [simulators/one_state.py](../../simulators/one_state.py).
Checks: [notebooks/one_state_simulator.ipynb](../../notebooks/one_state_simulator.ipynb).

## Words and units

- A **sitting** is one session of one subject: a schedule (perturbation and vision on
  every trial) and the movement angle on every trial.
- Everything is in units of the perturbation size, so $p_t \in \lbrace 0, +1, -1 \rbrace$.

## Equations

For trials $t = 1, \dots, T$:

```math
x_1 \sim \mathcal N(0, \sigma_\eta^2)
```

```math
y_t = x_t + \varepsilon_t, \qquad e_t = y_t + p_t, \qquad
x_{t+1} = A\, x_t - B\, v_t\, e_t + \eta_t
```

with $\varepsilon_t \sim \mathcal N(0, \sigma_\varepsilon^2)$ and
$\eta_t \sim \mathcal N(0, \sigma_\eta^2)$, all independent.

| Symbol | Meaning | Domain |
|---|---|---|
| $x_t$ | aiming angle: the movement plan (hidden) | |
| $y_t$ | movement angle: what the subject did (observed) | |
| $p_t$ | perturbation applied to the cursor | $0$, $+1$ or $-1$ |
| $e_t$ | error: where the cursor went, relative to the target | |
| $v_t$ | vision flag: 1 if the cursor is shown, 0 if not | $0$ or $1$ |
| $A$ | retention: fraction of the plan kept from one trial to the next | between 0 and 1 |
| $B$ | adaptation rate: fraction of the error corrected | between 0 and 1 |
| $\sigma_\eta$ | planning noise: standard deviation of the noise in the plan | positive |
| $\sigma_\varepsilon$ | execution noise: standard deviation of the noise in the movement | positive |

Parameter order in code: $\theta = (A, B, \sigma_\eta, \sigma_\varepsilon)$, named `A`,
`B`, `sigma_eta`, `sigma_epsilon`.

The execution noise $\varepsilon_t$ is part of the movement, and so of the error, so it is
fed back into the next plan. On a no-vision trial ($v_t = 0$) there is no error to learn
from: the plan decays by $A$ and picks up planning noise.

## Consequences used as checks

**Without noise,** with vision and a constant perturbation $p$, the movement approaches a
fixed point geometrically:

```math
y_{t+1} - y^* = (A - B)\,(y_t - y^*), \qquad y^* = -\frac{B\, p}{1 - A + B}
```

Without vision it only decays: $y_{t+1} = A\, y_t$.

**With noise,** under a constant perturbation the movements settle into a stationary
fluctuation around the fixed point. With vision the plan follows
$x_{t+1} - x^* = (A - B)(x_t - x^*) - B\,\varepsilon_t + \eta_t$, so its variance is
$V_x = (\sigma_\eta^2 + B^2 \sigma_\varepsilon^2) / (1 - (A - B)^2)$ and

```math
\sigma_y^2 = \sigma_\varepsilon^2 + V_x, \qquad
R(1) = \frac{(A - B)\, V_x - B\, \sigma_\varepsilon^2}{\sigma_y^2}
```

where $R(1)$ is the correlation between successive movements. The $-B\sigma_\varepsilon^2$
term is the execution noise of one trial being corrected on the next. Without vision
($B$ drops out):

```math
\sigma_y^2 = \sigma_\varepsilon^2 + \frac{\sigma_\eta^2}{1 - A^2}, \qquad
R(1) = \frac{A\, \sigma_\eta^2 / (1 - A^2)}{\sigma_y^2}
```

These are equations 9, 11 and 12 of the paper with the geometric sums added up. The
paper's equation 10, for $R(1)$ with vision, is printed differently: $+B\sigma_\varepsilon^2$
in the numerator, and $A^k (A - B)^k$ in place of $(A - B)^{2k}$ in the denominator. The
version above is derived here and agrees with simulation; the printed one does not
(`one_state_simulator.ipynb#[check-stationary]`).

## Priors

From [decision 0005](../decisions/0005-one-state-model-published-form.md). Each prior is
normal on an unbounded scale, with the stated range as its central 95% interval. The
constants are computed from the ranges in `one_state_priors.ipynb#[config]`.

| Quantity | Range (95%) | Prior |
|---|---|---|
| $A$ | 0.75 to 0.999 | $\mathrm{logit}(A) \sim \mathcal N(4.00, 1.48)$ |
| $B$ | 0.01 to 0.5 | $\mathrm{logit}(B) \sim \mathcal N(-2.30, 1.17)$ |
| $\sigma_\varepsilon$ | 1/15 to 1/3 | $\log \sigma_\varepsilon \sim \mathcal N(-1.90, 0.41)$ |
| $\sigma_\eta / \sigma_\varepsilon$ | 1/15 to 1/5 | $\log(\sigma_\eta/\sigma_\varepsilon) \sim \mathcal N(-2.16, 0.28)$ |

The second number of each normal is its standard deviation. $\sigma_\eta$ is the
execution noise times the ratio. Code: `sample_prior` in
[simulators/one_state.py](../../simulators/one_state.py).

## Schedules

A sitting is a sequence of blocks of four kinds: baseline ($p = 0$, $v = 1$),
perturbation $+1$ or $-1$ ($v = 1$), and no vision ($v = 0$, $p$ set to 0).

- 8 to 60 blocks, equally likely.
- Block lengths independent, $\log L \sim \mathcal N(3.11, 0.41)$ (central 95% interval
  10 to 50 trials), rounded to whole trials.
- The first block is a baseline. Each sitting draws its proportions of the four kinds
  from a symmetric Dirichlet with concentration 3; every later block's kind is drawn
  independently with those proportions. Neighbouring blocks of the same kind make one
  longer block.

Code: `sample_schedule` in [simulators/one_state.py](../../simulators/one_state.py),
which returns $p_t$ and $v_t$ for every trial. What the schedules look like:
[notebooks/one_state_priors.ipynb](../../notebooks/one_state_priors.ipynb).
