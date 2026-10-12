# 0008 — Two-state Model: the published two-rate form, states ordered through positive differences

**Date:** 2026-10-11, revised 2026-10-12 · **Status:** Proposed

**Context:** the posterior network recovers the parameters of the one-state Model
([PR #24](https://github.com/opherdonchin/MotorAdpatationSBI/pull/24)). The next question
([issue #28](https://github.com/opherdonchin/MotorAdpatationSBI/issues/28)) is whether
the same approach is feasible for a two-state Model, and that needs the Model and its
Prior fixed first. Opher's answers to the open points of the issue (2026-10-11): one
planning noise shared by the two states; the form the lab uses, which is the one of
Hulst et al. (2020); and the ordering of the two states expressed, as the lab does when
fitting in PyMC, through positive differences on the logit scale. The ranges of the
Prior are Opher's (review of
[PR #29](https://github.com/opherdonchin/MotorAdpatationSBI/pull/29), 2026-10-12).
Background, in plain words:
[Concept-two-state-model](https://github.com/opherdonchin/MotorAdpatationSBI/wiki/Concept-two-state-model).

Source: Hulst, Mamlins, Frens, Chang, Göricke, Timmann and Donchin (2020), *Can we
improve slow learning in cerebellar patients?*, bioRxiv,
[doi:10.1101/2020.07.03.185959](https://doi.org/10.1101/2020.07.03.185959). The form
below was read from the paper's public model code,
[thomashulst/paper-slowlearning](https://github.com/thomashulst/paper-slowlearning)
(`modelStateSpace.txt`). On 2026-10-12, with Opher's permission, it was compared with
the lab's private code, and the two agree on the Model. It is the two-state
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

| Symbol | In code | Meaning |
|---|---|---|
| $x^f_t$, $x^s_t$ | `x_fast`, `x_slow` | the fast and the slow part of the movement plan on trial $t$ (hidden) |
| $y_t$, $p_t$, $e_t$, $v_t$ | `y`, `p`, `e`, `v` | movement angle, perturbation, error and vision flag, as in 0005 |
| $A_f$, $A_s$ | `Af`, `As` | retention of the fast and of the slow state |
| $B_f$, $B_s$ | `Bf`, `Bs` | adaptation rate of the fast and of the slow state |
| $\sigma_\eta$ | `s_eta` | planning noise: standard deviation of the noise in each state |
| $\sigma_\varepsilon$ | `s_epsilon` | execution noise: standard deviation of the noise in the movement |

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
  code, named `Af`, `As`, `Bf`, `Bs`, `s_eta`, `s_epsilon`.
- **Domains.** The four rates between 0 and 1, ordered as above; the two standard
  deviations positive.
- **First state.** $x^f_1$ and $x^s_1$ each $\mathcal N(0, \sigma_\eta^2)$, independent,
  following 0005. (The paper gives each a wide normal prior and estimates it.)
- **Units, Task and Schedules.** As in 0005: units of the perturbation size; the Task
  and the Schedule Design of the one-state Model, unchanged.

**Prior.** It is stated in three steps, so that each number can be traced.

*Step 1: ranges for the rates themselves,* as numbers between 0 and 1. Each range is a
central 95% interval. These are the ranges the Prior is meant to have, and they keep the
two states apart: the highest fast retention is below the lowest slow one, and the
lowest fast adaptation rate is above the highest slow one.

| Rate | Range (95%) | As a time constant, $-1/\log A$ |
|---|---|---|
| $A_f$ | 0.70 to 0.90 | 3 to 9 trials |
| $A_s$ | 0.95 to 0.999 | 20 to 1,000 trials |
| $B_f$ | 0.10 to 0.35 | |
| $B_s$ | 0.001 to 0.05 | |

*Step 2: each range on the logit scale.* $\mathrm{logit}(r) = \log\big(r/(1-r)\big)$
takes a number between 0 and 1 to the whole line. A normal distribution there whose
central 95% interval is the logit of the range has mean halfway between the two logits
and standard deviation equal to their distance divided by $2 \times 1.96$.

| Rate | Logit of the range | Normal on the logit scale (mean, standard deviation) |
|---|---|---|
| $A_f$ | 0.85 to 2.20 | 1.52, 0.34 |
| $A_s$ | 2.94 to 6.91 | 4.93, 1.01 |
| $B_f$ | $-2.20$ to $-0.62$ | $-1.41$, 0.40 |
| $B_s$ | $-6.91$ to $-2.94$ | $-4.93$, 1.01 |

*Step 3: the slow rates through positive differences.* The fast rates are drawn from
their normals of step 2. The slow rates are not drawn directly. Each is the fast rate
moved by a positive difference on the logit scale:

```math
\mathrm{logit}(A_s) = \mathrm{logit}(A_f) + d_A, \qquad
\mathrm{logit}(B_s) = \mathrm{logit}(B_f) - d_B, \qquad d_A, d_B > 0
```

Each difference is given the mean and the variance that make the slow rate's logit come
out with the mean and variance of its row in step 2, the fast rate and the difference
being independent: the mean of $d_A$ is $4.93 - 1.52 = 3.40$ and its variance
$1.01^2 - 0.34^2 = 0.95^2$; the mean of $d_B$ is $-1.41 + 4.93 = 3.52$ and its variance
$1.01^2 - 0.40^2 = 0.93^2$. To be positive, each difference is log-normal with that mean
and variance (a log-normal with mean $m$ and variance $s^2$ has
$\sigma_{\log}^2 = \log(1 + s^2/m^2)$ and $\mu_{\log} = \log m - \sigma_{\log}^2/2$).

The Prior that results, with every part normal on an unbounded scale and the six draws
independent:

| Quantity | Prior | Median | Central 95% |
|---|---|---|---|
| $A_f$ | $\mathrm{logit}(A_f) \sim \mathcal N(1.52, 0.34)$ | 0.82 | 0.70 to 0.90 |
| $d_A$ | $\log d_A \sim \mathcal N(1.19, 0.27)$ | 3.29 | 1.9 to 5.6 |
| $B_f$ | $\mathrm{logit}(B_f) \sim \mathcal N(-1.41, 0.40)$ | 0.20 | 0.10 to 0.35 |
| $d_B$ | $\log d_B \sim \mathcal N(1.22, 0.26)$ | 3.39 | 2.0 to 5.6 |
| $\sigma_\varepsilon$ | $\log \sigma_\varepsilon \sim \mathcal N(-1.90, 0.41)$ | 0.149 | 1/15 to 1/3 |
| $\sigma_\eta / \sigma_\varepsilon$ | $\log(\sigma_\eta/\sigma_\varepsilon) \sim \mathcal N(-2.16, 0.28)$ | 0.115 | 1/15 to 1/5 |

The two noise rows are those of 0005.

*What the slow rates come out as.* A normal plus a log-normal is not exactly normal, so
the slow rates' ranges are close to those of step 1 and not equal to them (one-off
calculation, 2026-10-12, four million draws):

| Quantity | Asked for in step 1 | 2.5% | Median | 97.5% |
|---|---|---|---|---|
| $A_s$ | 0.95 to 0.999 | 0.964 | 0.992 | 0.9992 |
| $B_s$ | 0.001 to 0.05 | 0.0008 | 0.008 | 0.039 |
| slow time constant (trials) | 20 to 1,000 | 27 | 125 | 1,300 |
| slow time constant divided by fast | | 6 | 24 | 240 |
| adaptation reached under a constant perturbation (fraction of it) | | 0.41 | 0.69 | 0.95 |
| share of that adaptation held by the slow state | | 0.06 | 0.48 | 0.93 |

- **The states stay apart.** In four million draws, one had a slow time constant less
  than twice the fast one, and one had a slow adaptation rate above half the fast one.
- **Stability.** The Model is stable when $B_f/(1+A_f) + B_s/(1+A_s)$ is below 1;
  otherwise the movement swings from side to side with growing size. Under this Prior
  that quantity never exceeded 0.43 in four million draws, so nothing is truncated.

**Relation to the one-state Model.** The one-state Model of 0005 is not a special case
of this one. With a shared planning noise neither state can be switched off: each
always has its noise.

- *The nearest one-state behaviour* (Opher): when $B_s$ is very small, the slow state
  stops learning and is only its own noise, decaying by $A_s$. With $A_s$ well below 1
  it stays small. It is then noise added to the plan and little else changes: the Model
  behaves like a one-state Model with the fast state's rates and more noise than
  $\sigma_\eta$ alone. (The added noise is correlated from trial to trial, with
  variance $\sigma_\eta^2/(1 - A_s^2)$, so the match is close and not exact.)
- *An exact link, used as a Check of the code:* at the edge of the domain, when $A_f$
  and $A_s$ are equal, the plan $x^f_t + x^s_t$ follows the one-state Model with
  adaptation rate $B_f + B_s$ and planning noise $\sqrt 2\, \sigma_\eta$.

The Prior puts almost no weight near either case.

**Why:**

- *The published form* for the same reasons as in 0005: the symbols and sign are those
  of the paper, and one convention holds for all our Models. $y_t$ is the hand (the
  movement) and $e_t = y_t + p_t$ is the error (Opher, 2026-10-12).
- *Shared planning noise* (Opher): it is the published form, and it is the simpler
  start, with six parameters instead of seven.
- *Positive differences* (Opher): in the lab's experience this was the best
  parameterization for fitting in PyMC. The ordering holds by construction and nothing
  is truncated or rejected to get it. The fast rates are the ones drawn directly, and
  the differences move the slow rates away from them (confirmed by Opher, 2026-10-12).
  The paper orders the states by truncating the
  slow rate's prior at the fast rate; a hierarchical version would be awkward with
  that, and ours is meant to become hierarchical.
- *Ranges stated for the rates themselves, then translated* (Opher): the rates are what
  one has experience of; a range on a logit difference cannot be judged directly. The
  translation is written out so that it can be checked.
- *The Prior keeps the states apart* (Opher): a Prior under which a "slow" state can be
  as fast as a "fast" one gives posteriors that are degenerate in ways that are hard to
  debug later.
- *Log-normal differences:* positive, and normal on the log scale, so that the six
  quantities the network works with are all normal under the Prior. Agreed by Opher
  (2026-10-12).

*Alternatives:* recording the error as $y_t$, so that the learning term is $B\, y_t$
(tried for part of 2026-10-12 and reversed by Opher the same day: $y$ stays the hand, as
in 0005, and no existing Model, Sitting or Inference Engine changes); a planning noise for each state (seven parameters; left until the
shared one is understood); ordering by truncation, as in the paper (see above); no
ordering, with the labels sorted out afterwards (two modes in every posterior, which a
posterior network learns poorly); a free first state for each state, as in the paper
(two more parameters that one Sitting says little about); drawing the slow adaptation
rate directly and adding a positive difference to reach the fast one (it cannot give the
ranges of step 1: the fast rate's logit would then vary at least as much as the slow
one's, so $B_f$ would range over about 0.03 to 0.64 instead of 0.10 to 0.35; the rate
drawn directly has to be the one with the narrower range on the logit scale, which is
the fast one for both retention and adaptation rate); a difference that is normal
and cut off at zero (it would reproduce the slow rates' ranges of step 1 more closely,
but the quantity the network works with would no longer be normal); ranges stated
directly for the differences (the first draft of this record: it let the slow time
constant fall to 6 trials and the fast one rise to 20).

**Consequences:**

- Six parameters are estimated from the same data that carried four. The slow
  retention and the split of learning between the states are known to trade off against
  each other, so weaker contraction for some parameters is expected and is something
  [issue #28](https://github.com/opherdonchin/MotorAdpatationSBI/issues/28) reports.
- The posterior network will work with the six unbounded quantities of the Prior table
  (the two logits, the two log differences and the two logs for the noise), and results
  are reported for the six parameters. The transforms between the two are defined once,
  in `src/models/two_state.py`.
- The slow time constant reaches over a thousand trials at the top of the Prior, as
  long as the longest Sittings. Such values are hard to tell apart from perfect
  retention.
- The names `Af`, `As`, `Bf`, `Bs`, `s_eta`, `s_epsilon` differ from the one-state
  Model's `A`, `B`, `sigma_eta`, `sigma_epsilon`. Whether the one-state code is renamed
  to `s_eta` and `s_epsilon` is open.
