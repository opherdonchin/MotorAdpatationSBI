# 0002 — One-state model formulation for the first quick win

**Date:** 2026-10-01 · **Status:** Proposed

**Context:** The first quick win needs a motor-adaptation model simple enough to have an
exact likelihood, so BayesFlow's learned likelihood can be checked against ground truth,
yet realistic enough to matter.

**Decision:** A one-state linear-Gaussian model with both state and output noise, where
the learning signal is the error the subject actually observes:

```math
x_{t+1} = A\, x_t + B\,(p_t - y_t) + \eta_t, \qquad y_t = x_t + \varepsilon_t,
```

with $\eta_t \sim \mathcal N(0,\sigma_x^2)$, $\varepsilon_t \sim \mathcal N(0,\sigma_y^2)$
independent, $p_t$ the perturbation schedule, and parameters
$\theta = (A, B, \sigma_x, \sigma_y)$.

Confirmed by Opher (2026-10-01):

- **Initial state.** The state on the first trial is random, with the spread of the
  state noise: $x_1 \sim \mathcal N(0, \sigma_x^2)$. (Equivalently: the state is exactly
  0 before the experiment and takes one step of state noise.)
- **Domains.** $A, B \in (0, 1)$ and $\sigma_x, \sigma_y > 0$.
- **Priors on $A$ and $B$.** Normal on the log odds, so the boundaries are soft, with
  the mass in $0.75 < A < 0.999$ and $0.01 < B < 0.5$: the range that gives
  reasonable learning curves.
- **Schedules.** No fixed schedule. Each simulated sitting has its own length and its
  own schedule: $p_t$ is piecewise constant with values in $\{0, +1, -1\}$, block
  lengths are drawn from a distribution with soft boundaries and its mass between 10
  and 50 trials, and the value changes at random at every block boundary.

Still to confirm (the record stays *Proposed* until we do):

- What "the mass" means in numbers. Read as a central 95% interval, the priors are
  $\operatorname{logit} A \sim \mathcal N(4.00, 1.48)$ (median $A = 0.982$) and
  $\operatorname{logit} B \sim \mathcal N(-2.30, 1.17)$ (median $B = 0.091$), and a
  log-normal block length has median 22 trials (one-off calculation, 2026-10-01).
- Block boundaries: whether the value must change (to one of the other two values),
  and whether every sitting starts at 0.
- The distribution of the sitting length (number of trials, or number of blocks).
- Priors on $\sigma_x$ and $\sigma_y$, in units of the perturbation size.

**Why:** Including both noises was requested: the state noise makes the model a genuine
state-space problem rather than a deterministic curve plus noise. Using the observed error
$p_t - y_t$ is more realistic than a noiseless error, and it keeps an exact likelihood.

The reference likelihood is a Kalman filter in which $y_t$ is both the observation and a
known input. With $m_t, P_t$ the predicted mean and variance of $x_t$ given
$y_{1:t-1}$, starting from $m_1 = 0$, $P_1 = \sigma_x^2$:

```math
y_t \mid y_{1:t-1} \sim \mathcal N\left(m_t,\ P_t + \sigma_y^2\right)
```

```math
K_t = \frac{P_t}{P_t + \sigma_y^2},\quad m_{t\mid t} = m_t + K_t (y_t - m_t),\quad
P_{t\mid t} = (1 - K_t)\, P_t
```

```math
m_{t+1} = A\, m_{t\mid t} + B\,(p_t - y_t),\qquad P_{t+1} = A^2 P_{t\mid t} + \sigma_x^2
```

The order matters: update on $y_t$ first, then predict $x_{t+1}$ using the same $y_t$.
This is exact because, given $y_t$, the term $-B y_t$ is a known constant;
$x_{t+1}$ depends on the past only through $x_t$ and the observed $y_t$.

*Alternatives:* a noiseless error signal (simpler, less realistic); output noise only
(the likelihood becomes a product of independent Gaussians, too easy to be a test); a
known initial state $x_0 = 0$ and one fixed schedule (baseline, perturbation, washout),
both proposed first and replaced by the confirmed points above.

**Consequences:** $\sigma_x$ and $\sigma_y$ are expected to be only weakly identifiable
from each other; a correct learned likelihood should reproduce that ridge, not sharpen it.
The filter is to be verified against brute force (the exact joint Gaussian of a short
sequence) before it is trusted as the reference.

Because schedules and lengths vary, the schedule is an input to the learned likelihood
alongside the responses, and the network must handle sequences of different lengths.
In return, one trained network covers any schedule of this kind, including those of
real experiments, rather than a single design.
