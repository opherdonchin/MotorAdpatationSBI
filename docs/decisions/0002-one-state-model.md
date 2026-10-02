# 0002 — One-state model formulation for the first quick win

**Date:** 2026-10-01 · **Status:** Accepted

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

Everything is in units of the perturbation size: $p_t \in \{0, +1, -1\}$.

- **Initial state.** The state on the first trial is random, with the spread of the
  state noise: $x_1 \sim \mathcal N(0, \sigma_x^2)$. (Equivalently: the state is exactly
  0 before the experiment and takes one step of state noise.)
- **Domains.** $A, B \in (0, 1)$ and $\sigma_x, \sigma_y > 0$.
- **Priors.** The boundaries are soft: each prior is normal on an unbounded scale, with
  the stated range as its central 95% interval.

  | Quantity | Range (95%) | Prior | Median |
  |---|---|---|---|
  | $A$ | 0.75 to 0.999 | $\mathrm{logit}(A) \sim \mathcal N(4.00, 1.48)$ | 0.982 |
  | $B$ | 0.01 to 0.5 | $\mathrm{logit}(B) \sim \mathcal N(-2.30, 1.17)$ | 0.091 |
  | $\sigma_y$ | 1/15 to 1/3 | $\log \sigma_y \sim \mathcal N(-1.90, 0.41)$ | 0.149 |
  | $\sigma_x / \sigma_y$ | 1/15 to 1/5 | $\log(\sigma_x/\sigma_y) \sim \mathcal N(-2.16, 0.28)$ | 0.115 |

  The second number of each normal is its standard deviation. The state noise is given
  a prior through its ratio to the output noise, so $\sigma_x$ and $\sigma_y$ are
  dependent a priori; the implied $\sigma_x$ has median 0.017 and 95% interval 0.0065
  to 0.046. (Constants: one-off calculation, 2026-10-01.)
- **Schedules.** No fixed schedule. Each simulated sitting has 3 to 10 blocks, equally
  likely. $p_t$ is constant within a block. The first block is a baseline, $p_t = 0$;
  at every block boundary the value changes to one of the other two values, equally
  likely. Block lengths are log-normal with central 95% interval 10 to 50 trials
  ($\log L \sim \mathcal N(3.11, 0.41)$, median 22), rounded to whole trials.

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
both proposed first and replaced by Opher (2026-10-01).

The prior ranges come from experiments: $A$ and $B$ in the range that gives reasonable
learning curves; output noise of 3 to 10 degrees for an individual, against
perturbations of 30 to 45 degrees; state noise 1/15 to 1/5 of the output noise.

**Consequences:** $\sigma_x$ and $\sigma_y$ are expected to be only weakly identifiable
from each other; a correct learned likelihood should reproduce that ridge, not sharpen it.
With the state noise about a tenth of the output noise, the data will say
little about $\sigma_x$: its exact posterior may stay close to the prior, and recovery
has to be judged against that exact posterior, not against the true value.
The filter is to be verified against brute force (the exact joint Gaussian of a short
sequence) before it is trusted as the reference.

Because schedules and lengths vary, the schedule is an input to the learned likelihood
alongside the responses, and the network must handle sequences of different lengths.
In return, one trained network covers any schedule of this kind, including those of
real experiments, rather than a single design.
