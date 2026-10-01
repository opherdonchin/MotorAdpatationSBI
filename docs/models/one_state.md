# One-state model

A one-state linear-Gaussian model of motor adaptation with state noise and output noise.
Why this formulation, and where the prior ranges come from:
[decision 0002](../decisions/0002-one-state-model.md).

Code: [notebooks/explore_one_state.ipynb](../../notebooks/explore_one_state.ipynb)
(`#[sample-prior]`, `#[sample-schedule]`, `#[simulate-sitting]`, `#[kalman-logp]`).

## Words and units

- A **sitting** is one session of one subject: a perturbation schedule and the response
  on every trial. Trials are numbered $t = 1, \dots, T$. The likelihood is for a whole
  sitting.
- Everything is in units of the perturbation size, so $p_t \in \{0, +1, -1\}$.

## Equations

```math
x_1 \sim \mathcal N(0, \sigma_x^2)
```

```math
y_t = x_t + \varepsilon_t, \qquad \varepsilon_t \sim \mathcal N(0, \sigma_y^2)
```

```math
x_{t+1} = A\, x_t + B\,(p_t - y_t) + \eta_t, \qquad \eta_t \sim \mathcal N(0, \sigma_x^2)
```

All noise terms are independent. $x_t$ is the hidden state (the subject's compensation),
$y_t$ the observed response, $p_t$ the perturbation, and $p_t - y_t$ the error the subject
sees.

## Parameters

Order used in code: $\theta = (A, B, \sigma_x, \sigma_y)$.

| Parameter | Meaning | Domain |
|---|---|---|
| $A$ | retention: the fraction of the state kept from one trial to the next | $(0, 1)$ |
| $B$ | learning rate: the fraction of the observed error corrected | $(0, 1)$ |
| $\sigma_x$ | standard deviation of the state noise (and of the first state) | $> 0$ |
| $\sigma_y$ | standard deviation of the output noise | $> 0$ |

## Priors

Each prior is normal on an unbounded scale. The range is the central 95% interval, and
the constants follow from it (computed in the notebook's `#[config]`).

| Quantity | Range (95%) | Prior |
|---|---|---|
| $A$ | 0.75 to 0.999 | $\operatorname{logit} A \sim \mathcal N(4.003, 1.482)$ |
| $B$ | 0.01 to 0.5 | $\operatorname{logit} B \sim \mathcal N(-2.298, 1.172)$ |
| $\sigma_y$ | 1/15 to 1/3 | $\log \sigma_y \sim \mathcal N(-1.903, 0.411)$ |
| $\sigma_x / \sigma_y$ | 1/15 to 1/5 | $\log(\sigma_x/\sigma_y) \sim \mathcal N(-2.159, 0.280)$ |

The second number of each normal is its standard deviation. $\sigma_x$ has no prior of its
own: $\sigma_x = \sigma_y \cdot (\sigma_x/\sigma_y)$, so the two noise standard deviations
are dependent a priori.

## Schedules

Each sitting has its own schedule.

- The number of blocks is 3 to 10, equally likely.
- $p_t$ is constant within a block. The first block is a baseline, $p_t = 0$.
- At every block boundary $p_t$ changes to one of the other two values, equally likely.
- Block lengths are independent, $\log L \sim \mathcal N(3.107, 0.411)$ (central 95%
  interval 10 to 50 trials), rounded to whole trials.

## Exact likelihood

$m_t$ and $P_t$ are the mean and variance of $x_t$ given $y_{1:t-1}$, starting from
$m_1 = 0$, $P_1 = \sigma_x^2$. For each trial, in this order:

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

The log-likelihood of the sitting is the sum over trials of the log density in the first
line. The response $y_t$ is used twice: as the observation in the update, and as a known
input when predicting $x_{t+1}$.
