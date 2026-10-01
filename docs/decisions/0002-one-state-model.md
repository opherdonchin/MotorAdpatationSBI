# 0002 — One-state model formulation for the first quick win

**Date:** 2026-10-01 · **Status:** Proposed

**Context:** The first quick win needs a motor-adaptation model simple enough to have an
exact likelihood, so BayesFlow's learned likelihood can be checked against ground truth,
yet realistic enough to matter.

**Decision:** A one-state linear-Gaussian model with both state and output noise, where
the learning signal is the error the subject actually observes:

$$
x_{t+1} = A\,x_t + B\,(p_t - y_t) + \eta_t, \qquad y_t = x_t + \varepsilon_t,
$$

with $\eta_t \sim \mathcal N(0,\sigma_x^2)$, $\varepsilon_t \sim \mathcal N(0,\sigma_y^2)$
independent, $p_t$ a fixed perturbation schedule, and parameters
$\theta = (A, B, \sigma_x, \sigma_y)$.

Still to confirm (marked *proposed* until we do): initial state $x_0 = 0$ known exactly;
parameter domains $A, B \in (0, 1)$, $\sigma_x, \sigma_y > 0$; one fixed schedule
(baseline, perturbation, washout) for all simulated sittings.

**Why:** Including both noises was requested: the state noise makes the model a genuine
state-space problem rather than a deterministic curve plus noise. Using the observed error
$p_t - y_t$ is more realistic than a noiseless error, and it keeps an exact likelihood.

The reference likelihood is a Kalman filter in which $y_t$ is both the observation and a
known input. With $m_t, P_t$ the predicted mean and variance of $x_t$ given $y_{<t}$:

$$
y_t \mid y_{<t} \sim \mathcal N(m_t,\ P_t + \sigma_y^2),
$$

$$
K_t = \frac{P_t}{P_t + \sigma_y^2},\quad m_{t\mid t} = m_t + K_t (y_t - m_t),\quad
P_{t\mid t} = (1 - K_t) P_t,
$$

$$
m_{t+1} = A\,m_{t\mid t} + B\,(p_t - y_t),\qquad P_{t+1} = A^2 P_{t\mid t} + \sigma_x^2 .
$$

The order matters: update on $y_t$ first, then predict $x_{t+1}$ using the same $y_t$.
This is exact because, given $y_t$, the term $-B y_t$ is a known constant;
$x_{t+1}$ depends on the past only through $x_t$ and the observed $y_t$.

*Alternatives:* a noiseless error signal (simpler, less realistic); output noise only
(the likelihood becomes a product of independent Gaussians, too easy to be a test).

**Consequences:** $\sigma_x$ and $\sigma_y$ are expected to be only weakly identifiable
from each other; a correct learned likelihood should reproduce that ridge, not sharpen it.
The filter is to be verified against brute force (the exact joint Gaussian of a short
sequence) before it is trusted as the reference.
