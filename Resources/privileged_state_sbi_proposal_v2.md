# Simulation-Based Whole-Sitting Likelihoods for Hierarchical Motor-Adaptation Models

**Revised proposal for external review**  
**Date:** 2026-09-27

## Executive summary

This project aims to turn a sequential scientific simulator into a reusable, differentiable **whole-sitting likelihood** suitable for hierarchical Bayesian inference.

The first implementation target is a bounded sCOIN-class motor-adaptation simulator, preceded by one-state and two-state linear-Gaussian benchmarks. Full nonparametric COIN is **out of scope** for the present project. The present proposal also starts from an already implemented simulator; automatic translation from mathematical model specification to simulator code is a separate future problem.

The revised proposal is deliberately **baseline first**. It no longer assumes that privileged simulator state or a bespoke representation hierarchy is necessary. The primary baseline uses BayesFlow neural likelihood-to-evidence ratio estimation (NRE-C) directly on the observed sequence. If that standard approach is accurate, calibrated, fast enough, and robust under the intended hierarchical analyses, the project should stop there.

Privileged simulator state is treated as optional training-time information whose benefit must be demonstrated by matched ablations. The custom Markov-aware contribution has also been reduced to its essential form:

\[
a_t \longrightarrow r_t \longrightarrow s_t,
\]

where \(a_t\) is a complete simulator transition, \(r_t\) is a local transition representation, and \(s_t\) is a compressed local privileged representation. Standard BayesFlow sequence summarization then handles the remaining variable-length sequence compression.

The proposed experimental ladder is:

\[
\boxed{
A:\ \text{observed-only BayesFlow NRE}
}
\]

\[
\boxed{
A^+:\ \text{observed-only NRE + privileged auxiliary supervision}
}
\]

\[
\boxed{
B:\ \text{generic privileged BayesFlow teacher}
}
\]

\[
\boxed{
C:\ \text{generic BayesFlow after Markov-aware }a\to r\to s
}
\]

\[
\boxed{
D:\ \text{infer the temporally resolved privileged } \mathbf s
\text{ rather than the final privileged summary}
}
\]

\[
\boxed{
E:\ \text{add explicit privileged-state retention regularization}
}
\]

Each added stage is authorized only after the simpler stage fails a predeclared requirement or the added stage produces a meaningful improvement at matched simulator budget and compute.

The common downstream target is a sitting-level log likelihood,

\[
\ell(\theta;Y,U)
=
\log p(Y\mid\theta,U)+C(Y,U),
\]

where the additive constant is independent of \(\theta\). BayesFlow NRE estimates this likelihood shape directly. HSSM or low-level PyMC then consumes the learned factor for hierarchical inference. Whether HSSM is preferable to direct PyMC is now an **engineering decision**, not a methodological premise.

---

# 1. Scope and deliverable

## 1.1 Product in scope

The present product is

\[
\boxed{
\text{scientific simulator}
\longrightarrow
\text{validated whole-sitting likelihood surrogate}.
}
\]

The user supplies:

- a parameter vector \(\theta\);
- an ordered trial specification \(U=(u_0,\ldots,u_T)\);
- a simulator that generates observations \(Y=(y_0,\ldots,y_T)\);
- optionally, for privileged procedures, the simulator's propagated latent state
  \(X=(x_0,\ldots,x_T)\).

The product returns a differentiable function

\[
\boxed{
\widehat \ell(\theta;Y,U)
}
\]

that approximates

\[
\log p(Y\mid\theta,U)
\]

up to a constant independent of \(\theta\), over a declared parameter/design domain.

The intended consumer is a hierarchical probabilistic program in HSSM or PyMC.

## 1.2 Product not in scope

This revision does **not** claim to translate arbitrary mathematical model descriptions automatically into correct simulators. Model-to-simulator translation is a separate future layer.

Full unbounded/nonparametric COIN is also out of scope. The first difficult target is a **named, versioned, bounded sCOIN simulator** with a declared finite context representation.

## 1.3 Hierarchical reuse is scoped, not arbitrary

The learned sitting factor can be reused under different hierarchical priors only within the simulator/training domain and under the following assumptions:

1. empirical sittings are conditionally independent given the modeled parameters and declared reset/initial-state law;
2. all hierarchical effects that should vary in the later model enter through exposed parameters or explicit conditioning variables;
3. nuisance quantities marginalized under a fixed simulator/training distribution are not later silently assigned a new hierarchy;
4. the later hierarchy stays inside the parameter support and design envelope on which the ratio estimator was validated;
5. discrete scientific parameters require explicit marginalization or a suitable mixed sampler rather than ordinary NUTS updates.

The learned factor is not a normalized generative density in \(Y\), because its evidence normalization is unknown. It is therefore not directly suitable for cross-model Bayes factors. Posterior predictive simulation should use the original scientific simulator.

---

# 2. Statistical target

## 2.1 Training distribution

For the initial project scope,

\[
\theta\sim\pi_0(\theta),
\qquad
U\sim\rho(U),
\]

independently, followed by

\[
(X,Y)\sim p(X,Y\mid\theta,U).
\]

Thus

\[
p_0(\theta,U,X,Y)
=
\pi_0(\theta)\rho(U)p(X,Y\mid\theta,U).
\]

The distribution \(\pi_0\) is a **training/coverage distribution**, not necessarily the final scientific prior. It must have an evaluable density and cover the parameter region later hierarchies may visit.

The design distribution \(\rho(U)\) must cover the intended sequence lengths, perturbation/cue schedules, conditions, and design families.

## 2.2 Likelihood-to-evidence ratio

Let

\[
Z=(Y,U).
\]

NRE targets

\[
r_Y(\theta;Y,U)
=
\frac{p(Y,U\mid\theta)}
     {p_0(Y,U)}.
\]

Because the initial training design assumes

\[
U\perp\theta,
\]

we have

\[
p(Y,U\mid\theta)
=
\rho(U)p(Y\mid\theta,U)
\]

and

\[
p_0(Y,U)
=
\rho(U)p_0(Y\mid U).
\]

Therefore

\[
\boxed{
r_Y(\theta;Y,U)
=
\frac{p(Y\mid\theta,U)}
     {p_0(Y\mid U)}.
}
\]

For fixed \(Y,U\),

\[
\boxed{
\log r_Y(\theta;Y,U)
=
\log p(Y\mid\theta,U)
+
C(Y,U).
}
\]

Thus a calibrated NRE model already provides the likelihood shape required by MCMC; there is no need to divide an approximate posterior by \(\pi_0\).

BayesFlow's `RatioApproximator` implements contrastive NRE-C and directly exposes the estimated log likelihood-to-evidence ratio.

## 2.3 Boundary of the independence assumption

The cancellation above depends on \(U\perp\theta\) in the training process.

Adaptive or informative designs, stopping rules, or staircase procedures that make \(U\) depend on latent/model parameters require a revised conditional-ratio construction or explicit modeling of the design process. They are not silently covered by the initial implementation.

## 2.4 Secondary posterior cross-check

For Procedure A only, also train a conventional BayesFlow neural posterior estimator

\[
q_0(\theta\mid Y,U).
\]

Then compare

\[
\log q_0(\theta\mid Y,U)-\log\pi_0(\theta)
\]

with the NRE log-ratio surface.

This is not the primary deployment route. It is an independent estimator whose agreement with NRE provides useful evidence on the load-bearing baseline.

---

# 3. Common software architecture

## 3.1 BayesFlow upstream

BayesFlow is the common SBI framework.

For ordered variable-length sequences, the initial summary-network candidate is `TimeSeriesTransformer`, which maps a masked tensor of shape

\[
(\text{batch},T,\text{features})
\]

to a fixed-dimensional summary. `FusionTransformer` and the lighter `TimeSeriesNetwork` are predeclared alternatives if sequence length, simulation budget, or compute makes the default inappropriate.

The observed per-trial input is

\[
z_t^Y=(y_t,u_t).
\]

Thus the design sequence is learned jointly with the behavioral sequence rather than compressed separately by default.

The privileged generic input is

\[
z_t^P=(x_t,y_t,u_t)
\]

after model-specific serialization of \(x_t\).

BayesFlow's `RatioApproximator` is the default likelihood-ratio estimator.

## 3.2 HSSM or PyMC downstream

HSSM already documents BayesFlow NRE integration through both ONNX and JAX-callable routes. Its approximate differentiable ONNX contract expects a fixed-dimensional row and returns one scalar contribution. After sequence summarization, we can treat

\[
\boxed{
\text{one experimental sitting}=\text{one likelihood row}.
}
\]

The current HSSM contract is therefore not automatically disqualifying: the variable-length sequence is handled upstream and the downstream row is fixed-dimensional.

However, HSSM is no longer assumed to be the necessary consumer. Before committing to it, perform a small integration spike implementing the same learned ratio in:

1. HSSM using a custom model / JAX callable or ONNX route;
2. low-level PyMC using an explicit differentiable custom factor.

Choose HSSM only if its formula/regression/hierarchical interface materially simplifies the intended analyses without forcing an awkward sitting-as-trial representation or limiting the surrogate. Otherwise use PyMC directly.

This consumer choice must not alter the scientific comparison among Procedures A-E.

---

# 4. Simulator requirements

## 4.1 Requirements for Procedure A

The observed-only baseline needs only a scientifically correct simulator that maps

\[
(\theta,U,\xi)\rightarrow Y,
\]

with reproducible random-number control and a documented parameter/design domain.

## 4.2 Additional privileged-state contract for Procedures B-E

For the Markov-aware procedures, the simulator must expose a complete propagated state.

Initialization:

\[
(\theta,u_0,\xi_0)
\longrightarrow
(x_0,y_0).
\]

Transition:

\[
(x_{t-1},y_{t-1},u_t,\theta,\xi_t)
\longrightarrow
(x_t,y_t).
\]

The transition must have no scientifically relevant hidden persistent state outside its explicit inputs. Anything affecting future simulation—context identity, context-specific memories, a transition matrix drawn once per sitting, counters, etc.—must be contained in \(x_t\), \(\theta\), or an explicit conditioning object.

A serialized state should permit checkpoint/restart continuation.

### Required tests

Passing restart tests is necessary but not sufficient.

Validate both:

1. **software state completeness:** checkpoint/restart, changed call order, fresh process, controlled RNG, mutation tests;
2. **scientific correctness:** reference trajectories, transition-distribution checks, known limiting cases, and comparisons with the published/accepted simulator.

A simulator can be perfectly restartable and scientifically wrong.

---

# 5. Procedure A — observed-only BayesFlow NRE

This is the load-bearing baseline.

## 5.1 Input and summary

For sitting \(i\),

\[
Z_i^Y=
\bigl(
(y_{i0},u_{i0}),
\ldots,
(y_{iT_i},u_{iT_i})
\bigr).
\]

Map

\[
Z_i^Y
\xrightarrow[
\max\ J_A
]
{\text{BayesFlow TimeSeriesTransformer}}
C_i^Y
\in\mathbb R^{d_C}.
\]

`TimeSeriesTransformer` is the first implementation. Use masks for padded variable-length batches. `FusionTransformer` or `TimeSeriesNetwork` are escalation options.

## 5.2 Ratio estimation

Train

\[
(\theta_i,C_i^Y)
\xrightarrow[
\max\ J_A
]
{\text{BayesFlow RatioApproximator / NRE-C}}
\widehat{\log r}_A(\theta_i;Y_i,U_i).
\]

The summary network and ratio network are trained jointly by BayesFlow's contrastive NRE-C objective.

## 5.3 Hyperparameter tuning

Tune:

\[
d_C,
\]

summary-network size, NRE hidden width/depth, NRE-C contrastive hyperparameters, and regularization.

Use the smallest configuration whose validation likelihood-ratio metrics are statistically indistinguishable from the best candidate.

Start with BayesFlow's Base time-series configuration rather than an unrestricted architecture search.

## 5.4 Required validation

On exact benchmarks:

- RMS and maximum error of
  \[
  \Delta\log L(\theta)
  \]
  relative to a fixed anchor;
- gradient error
  \[
  \nabla_\theta\Delta\log L;
  \]
- posterior recovery from
  \[
  \widehat p_0(\theta\mid Y,U)
  \propto
  \widehat r_A(\theta;Y,U)\pi_0(\theta);
  \]
- SBC plus data-sensitive diagnostics;
- coverage and contraction;
- performance stratified by sitting length and design family.

Also train the NPE cross-check for Procedure A and compare its posterior/prior-derived likelihood shape with NRE.

## 5.5 What A tests

Procedure A asks:

\[
\boxed{
\text{Can standard observed-only BayesFlow already learn the required whole-sitting likelihood?}
}
\]

If yes at the required accuracy, calibration, simulation budget, and hierarchical runtime, privileged-state development is optional research rather than a product requirement.

---

# 6. Procedure \(A^+\) — observed NRE with privileged auxiliary supervision

Procedure \(A^+\) uses \(X\) **only during training**. There is no privileged representation to marginalize at deployment.

## 6.1 Architecture

Keep the same observed sequence and final ratio estimator as A.

Expose time-resolved internal sequence features

\[
h_t^Y
\]

from the observed summary network.

Attach an auxiliary head that predicts selected simulator-state components from

\[
(h_t^Y,U).
\]

Use model-appropriate losses:

- standardized squared error or Gaussian prediction for continuous stochastic states;
- cross-entropy for discrete context/state labels;
- masks for absent/padded state components.

Do not require reconstruction of deterministic coordinates merely because they were present in the encoder input.

## 6.2 Objective

\[
\boxed{
J_{A^+}
=
J_{\mathrm{NRE}}
-
\lambda L_X.
}
\]

Search a small predeclared grid of \(\lambda\), including \(\lambda=0\).

At deployment the auxiliary head and \(X\) disappear:

\[
(Y,U)\rightarrow C^Y\rightarrow \widehat r(\theta;Y,U).
\]

## 6.3 What \(A^+\) tests

A versus \(A^+\) asks:

\[
\boxed{
\text{Does privileged state help purely as training-time supervision?}
}
\]

This is the cheapest privileged-state test and should precede construction of a separate privileged latent space.

---

# 7. Procedure B — generic privileged BayesFlow teacher

Procedure B introduces a privileged representation but gives it **no hand-designed Markov-aware architecture**.

## 7.1 Privileged summary

Serialize each privileged trial as

\[
z_t^P=(x_t,y_t,u_t).
\]

Map the complete privileged sequence through an ordinary BayesFlow time-series summary:

\[
Z^P
\xrightarrow[
\max\ J_B^P
]
{\text{BayesFlow TimeSeriesTransformer}}
C^P.
\]

Then train a privileged NRE model

\[
(\theta,C^P)
\longrightarrow
\widehat r_P(\theta;C^P).
\]

This estimates a ratio based on the compressed complete trajectory.

## 7.2 Observed-to-privileged bridge

Freeze the privileged teacher. For each simulation obtain its teacher target \(C_i^P\).

Train

\[
(Y,U)
\xrightarrow{
\text{BayesFlow conditional density model}
}
q_{YU,C^P}(C^P\mid Y,U).
\]

Because \(C^P\) is fixed-dimensional, begin with a conditional Gaussian or Gaussian mixture; escalate to a conditional flow if held-out conditional density and coverage require it.

## 7.3 Observed likelihood approximation

For a new sitting, draw

\[
C_r^P
\sim
q_{YU,C^P}(C^P\mid Y,U),
\qquad r=1,\ldots,R.
\]

Approximate

\[
\boxed{
\widehat r_B(\theta;Y,U)
=
\frac1R
\sum_{r=1}^{R}
\widehat r_P(\theta;C_r^P).
}
\]

Use fixed draws for all subsequent MCMC evaluations.

## 7.4 Important qualification

At the raw complete-data level,

\[
r_Y(\theta;Y,U)
=
E_{p_0(X\mid Y,U)}
\left[
r_{\mathrm{complete}}(\theta;X,Y,U)
\right].
\]

Procedure B replaces the complete trajectory by a learned summary \(C^P\). Therefore the mixture above is **not automatically exact**. It depends on:

1. \(C^P\) preserving the complete-data ratio information relevant to \(\theta\);
2. \(q(C^P\mid Y,U)\) approximating the induced privileged-summary distribution.

Both are empirical claims.

## 7.5 What B tests

A versus B asks:

\[
\boxed{
\text{Does a generic privileged teacher improve the final observed likelihood?}
}
\]

But a negative B result must be interpreted narrowly:

\[
\boxed{
\text{privileged information did not help through a generic sequence representation.}
}
\]

It does **not** prove privileged state has no useful information; that is why \(A^+\) and C are separate tests.

---

# 8. Procedure C — Markov-aware privileged local encoding

Procedure C changes only the privileged encoder used in B.

## 8.1 Local complete transition

Define

\[
a_0=(\mathrm{init},u_0,x_0,y_0)
\]

and for \(t\ge1\),

\[
a_t=
(\mathrm{transition},
x_{t-1},y_{t-1},u_t,x_t,y_t).
\]

Because \(x_t\) is required to be the complete propagated state, each \(a_t\) is a local complete-data transition.

## 8.2 Shared Markov-aware encoder

Use the same deterministic maps at every transition:

\[
a_t
\xrightarrow{
f_{aR}(\cdot;\omega_{aR})
}
r_t
\in\mathbb R^{d_R},
\]

\[
r_t
\xrightarrow{
f_{R s}(\cdot;\omega_{Rs})
}
s_t
\in\mathbb R^{d_s}.
\]

Initial implementation:

- \(f_{aR}\): shared residual MLP;
- \(f_{Rs}\): linear bottleneck plus one residual MLP block, or similar.

The complete privileged sequence is

\[
\mathbf s=(s_0,\ldots,s_T).
\]

There is no privileged bidirectional \(H\) layer. If the simulator state contract holds, complete-data evidence is local. Past/future sequence integration remains the job of the generic BayesFlow summary after the local Markov-aware encoding.

## 8.3 Standard BayesFlow after the custom local encoder

Do **not** impose the previous bespoke

\[
\mathbf s\rightarrow S\rightarrow W
\]

hierarchy by default.

Instead:

\[
\mathbf s
\xrightarrow{
\text{BayesFlow TimeSeriesTransformer}
}
C^P
\]

followed by the same privileged NRE model as B:

\[
(\theta,C^P)
\rightarrow
\widehat r_P(\theta;C^P).
\]

All local encoder and BayesFlow weights are trained end-to-end through the privileged NRE objective.

The observed bridge remains exactly as in B:

\[
(Y,U)\rightarrow q(C^P\mid Y,U).
\]

## 8.4 What C tests

B versus C isolates:

\[
\boxed{
\text{Does explicitly exposing complete local Markov transitions improve privileged representation learning?}
}
\]

The comparison should use matched simulation banks, similar parameter counts where practical, and identical downstream bridge/ratio machinery.

A negative B followed by positive C is evidence for an inductive-bias/sample-efficiency benefit, not evidence that privileged information was absent from the generic input.

---

# 9. Procedure D — temporally resolved privileged bridge

Procedure D keeps Procedure C's privileged model but moves the observed/privileged bridge earlier.

## 9.1 Observed target

Instead of

\[
(Y,U)\rightarrow q(C^P\mid Y,U),
\]

learn

\[
\boxed{
(Y,U)
\rightarrow
q(\mathbf s\mid Y,U),
}
\]

where

\[
\mathbf s=(s_0,\ldots,s_T)
\]

is the temporally resolved privileged representation.

The observed conditioner should use a whole-sequence BayesFlow time-series network. The conditional target over \(\mathbf s\) can initially use an autoregressive Gaussian-mixture model or autoregressive flow.

## 9.2 Reference-measure gate

This procedure is authorized only after inspecting the conditional geometry of \(\mathbf s\mid Y,U\).

A deterministic privileged encoder can produce components of \(\mathbf s\) that become deterministic once \(Y,U\) are fixed. A full-dimensional nonsingular Gaussian mixture or ordinary normalizing flow is then a misspecified density model.

Before training D:

1. inspect conditional covariance/intrinsic-rank structure on repeated simulations;
2. identify any coordinates that are deterministic functions of known \(Y,U\);
3. either remove/condition on those coordinates, parameterize only the stochastic coordinates, or introduce an explicit fixed dequantization/noise model and acknowledge the changed target.

"Use a larger network" is not a solution to a singular conditional distribution.

## 9.3 Marginalization

For fixed empirical \((Y,U)\), generate

\[
\mathbf s_r
\sim
q(\mathbf s\mid Y,U).
\]

Then

\[
\mathbf s_r
\rightarrow
C_r^P
\rightarrow
\widehat r_P(\theta;C_r^P).
\]

Approximate

\[
\boxed{
\widehat r_D(\theta;Y,U)
=
\frac1R
\sum_r
\widehat r_P(\theta;C_r^P).
}
\]

## 9.4 What D tests

C versus D asks:

\[
\boxed{
\text{Is the temporally resolved privileged sequence easier or more reliable to infer from observations than the final compressed privileged summary?}
}
\]

D incurs substantially greater density-estimation and integration complexity and therefore requires a meaningful benefit over C.

---

# 10. Procedure E — privileged-state retention regularization

The previous proposal described a full backward density

\[
q(X,Y\mid\mathbf s,U).
\]

That target can be singular or reward variance collapse when deterministic encoded quantities are reconstructed. This revision does not assume such a density is well defined.

Instead E adds a clearly auxiliary **state-retention objective**.

## 10.1 Auxiliary targets

For each model family, declare which privileged-state components are:

- continuous stochastic state;
- discrete stochastic state/context labels;
- deterministic/derived quantities;
- fixed known inputs.

Use \(\mathbf s\) or \(s_t\) to predict only prespecified privileged targets with an explicit loss/reference measure.

Examples:

- standardized MSE or fixed-variance Gaussian loss for continuous states;
- cross-entropy for discrete context labels;
- masked prediction of selected transition quantities.

The loss is a regularizer, not a claim to represent the exact conditional density of the entire simulator trajectory.

## 10.2 Objective

\[
\boxed{
J_E
=
J_{\mathrm{privileged\ NRE}}
-
\lambda_E L_{\mathrm{retain}}.
}
\]

Tune \(\lambda_E\), including zero, on held-out final likelihood accuracy and calibration.

## 10.3 What E tests

D versus E asks:

\[
\boxed{
\text{Does forcing the privileged local representation to retain declared simulator-state information improve the final observed-data likelihood?}
}
\]

A better reconstruction score by itself is not success. E is retained only if final likelihood quality, calibration, or simulation efficiency improves.

---

# 11. Optional privileged-information control: joint score or joint ratio

If a simulator can evaluate additional joint quantities such as

\[
\nabla_\theta \log p(X,Y\mid\theta,U)
\]

or a joint likelihood ratio, use simulator-augmented SBI methods as an additional privileged baseline.

Such information can be more directly useful than the latent state itself and may require far less custom architecture. This control is optional because many scientific simulators expose trajectories without exposing tractable joint likelihoods or derivatives.

---

# 12. Calibration and validation

## 12.1 Ratio calibration is required at every rung

NRE avoids explicit posterior/prior division but introduces classifier/ratio-estimation error.

For every A-E candidate, reconstruct

\[
\widehat p_0(\theta\mid Y,U)
\propto
\widehat r(\theta;Y,U)\pi_0(\theta)
\]

and assess:

- simulation-based calibration;
- coverage of prespecified marginal and multivariate intervals;
- parameter recovery where identifiable;
- posterior contraction with increasing information;
- data-dependent test quantities, not only parameter ranks;
- design- and length-stratified diagnostics.

Ordinary SBC alone is insufficient: an estimator that ignores the data and returns the prior can satisfy some rank diagnostics.

## 12.2 Exact/reference likelihood checks

For the one-state and two-state benchmarks, derive or implement the correct reference likelihood for the exact timing, feedback, initialization, and noise structure used by the simulator.

Do not import a textbook Kalman formula without checking that the error-feedback formulation has the required independence/covariance structure.

Compare

\[
\Delta \log L(\theta)
=
\log L(\theta)-\log L(\theta_{\mathrm{anchor}})
\]

and its gradients over the scientifically relevant parameter region.

## 12.3 Hierarchical accumulation tests

Small systematic sitting-level log-ratio errors can accumulate across many sittings.

Therefore simulate full hierarchical datasets at the intended range of \(N\), fit them under:

- the training prior;
- narrower shifted priors;
- heavier-tailed priors within the validated support;
- different subject/condition regressions.

Compare group- and subject-level posteriors with the reference method.

## 12.4 Training-domain checks

For \(\pi_0\) and \(\rho(U)\), report:

- coverage plots;
- simulator plausibility failures;
- design/length support;
- parameter-transform Jacobians where relevant;
- performance near parameter-domain boundaries.

The validity statement for the trained likelihood must name this deployment envelope.

---

# 13. Numerical deployment

## 13.1 Procedure A and \(A^+\)

The deployment object is simply

\[
(\theta,C^Y)
\rightarrow
\widehat{\log r}_A.
\]

Compute \(C^Y\) once per empirical sitting.

This is the preferred operational form because it requires one fixed-dimensional surrogate evaluation per sitting per likelihood call.

## 13.2 Procedures B and C

Generate a fixed collection

\[
C_{jr}^P
\sim
q(C^P\mid Y_j,U_j)
\]

once for each empirical sitting.

Then

\[
\widehat r_j(\theta)
=
\frac1R
\sum_r
\widehat r_P(\theta;C_{jr}^P).
\]

Use stable `logsumexp`.

## 13.3 Procedure D/E

Generate fixed bridge samples

\[
\mathbf s_{jr}
\sim q(\mathbf s\mid Y_j,U_j)
\]

and precompute

\[
C_{jr}^P
=
f_{\mathrm{BF}}(\mathbf s_{jr}).
\]

Only the ratio head is evaluated during NUTS.

## 13.4 Fixed Monte Carlo versus QMC

Use fixed pseudorandom Monte Carlo as the baseline.

Randomized scrambled Sobol/QMC is tested only if the bridge sampling transform is sufficiently continuous and empirical convergence improves. Discrete mixture selection can reduce QMC effectiveness.

For any bridge-based method:

- double \(R\);
- use independent fixed sample sets/scrambles;
- compare log ratios and gradients;
- test along posterior paths under changed priors.

Increasing \(R\) controls numerical integration error, not learned-network bias.

## 13.5 Integration compression if needed

If the \(N\times R\) ratio evaluations make NUTS too slow, test only after correctness is established:

- weighted prototype reduction of \(C_r^P\);
- per-sitting distillation of the finite mixture to a smaller differentiable surrogate.

Any compression must be validated against the explicit high-\(R\) mixture in both log density and gradient.

---

# 14. HSSM-versus-PyMC consumer gate

Before large-scale fitting, use the same validated Procedure-A ratio callable in two minimal hierarchical implementations.

## HSSM route

Use HSSM's documented BayesFlow NRE/JAX or ONNX integration. Represent one sitting by one fixed-dimensional summary row.

Measure:

- amount of adapter/configuration code;
- support for subject/condition regressions;
- compatibility with the desired response/summary columns;
- gradient latency;
- NUTS ESS per second;
- restrictions imposed by ONNX/JAX export.

## PyMC route

Implement the same ratio as a differentiable PyMC factor/custom distribution.

Measure the same quantities.

## Decision

Choose HSSM if its hierarchical/formula interface materially reduces implementation and analysis complexity without constraining the surrogate.

Otherwise use PyMC directly.

HSSM is therefore a candidate reusable consumer, not a scientific dependency of the proposed SBI method.

---

# 15. Benchmark sequence and gates

## 15.1 Benchmark 0: backend/integration smoke test

Use a very small exactly evaluable Gaussian sequential model.

Tasks:

1. train Procedure A;
2. compare source BayesFlow ratio to exported/JAX ratio;
3. fit a tiny hierarchical model in HSSM and PyMC;
4. confirm identical posterior target and gradients within numerical tolerance.

This tests software integration, not scientific adequacy.

## 15.2 Benchmark 1: one-state adaptation model

Use the exact simulator actually intended, including feedback timing and initialization.

Evaluate A first.

Only run \(A^+\) or later procedures if A fails a required accuracy/calibration/efficiency criterion or if the explicit research goal is to quantify privileged-state gains.

For privileged arms, compare learned local representations against known complete-data regression/sufficient-statistic structure as a diagnostic, not as a required coordinate system.

## 15.3 Benchmark 2: two-state fast/slow model

This is the first benchmark with meaningful latent decomposition and weak-identifiability concerns.

Compare:

\[
A,\quad A^+,
\]

and only if warranted,

\[
B,\ C,\ D,\ E.
\]

Evaluate label convention, multimodality, correlated parameters, changed priors, and simulation efficiency.

## 15.4 Benchmark 3: bounded sCOIN

Before starting, freeze:

- simulator code/version;
- scientific parameterization;
- maximum/fixed context representation;
- masks/serialization;
- declared \(T\) and design ranges;
- reference solver and tolerances.

If the available sCOIN analysis is itself approximate, establish a high-precision reference procedure with convergence evidence rather than calling it exact.

Full nonparametric COIN is not part of Benchmark 3.

## 15.5 General-tooling test

After success on bounded sCOIN, have a model author who did not implement the core framework onboard a second nontrivial simulator using only the documented adapter interface.

Record:

- custom code required;
- implementation time;
- simulator changes;
- errors/failures;
- retraining decisions.

Success on one sCOIN implementation does not by itself demonstrate a general simulator-to-likelihood tool.

---

# 16. Predeclared go/no-go rules

The exact thresholds should be ratified before benchmark results are examined. The following are provisional starting values proposed by the reviews.

## 16.1 Exact benchmark likelihood

Across a prespecified parameter grid/domain:

\[
\mathrm{RMS}\bigl(
\Delta\log\widehat L-\Delta\log L_{\mathrm{ref}}
\bigr)
<0.1
\]

and

\[
\max
\left|
\Delta\log\widehat L-\Delta\log L_{\mathrm{ref}}
\right|
<0.5.
\]

These must be tightened if hierarchy-scale experiments show the residual error is consequential.

## 16.2 Posterior recovery

Against a reliable reference:

- posterior-mean error \(<0.1\) reference posterior SD;
- posterior-SD error \(<10\%\);
- no material systematic calibration departure beyond Monte Carlo uncertainty;
- explicit multivariate/mode checks when posterior structure is non-Gaussian.

## 16.3 Proceeding beyond A

Do not build a more complex privileged method merely because A is imperfect.

First diagnose whether failure is due to:

- simulator error;
- unsupported design/parameter domain;
- insufficient training simulations;
- summary-network capacity;
- ratio-network capacity/calibration;
- consumer/backend error.

A custom privileged stage is authorized only for a reproducible failure attributable to representation/inference limitations that privileged information plausibly addresses.

## 16.4 Keeping additional complexity

An added procedure should survive matched-budget ablation and provide a practically meaningful advantage, for example:

\[
\boxed{
\ge 2\times
\text{ reduction in simulator calls at equal inference quality}
}
\]

or repair a required capability that the simpler procedure cannot meet.

A small local-loss improvement is insufficient.

## 16.5 Consumer runtime

Declare an end-to-end hierarchical runtime/ESS target after profiling Benchmark 0. Report:

- likelihood and gradient latency per sitting;
- NUTS ESS/s;
- scaling with \(N\);
- bridge-sample scaling with \(R\), if applicable.

---

# 17. Method-selection discipline

For every stage:

1. use shared simulation banks across methods;
2. maintain train/validation/untouched test splits by complete sitting;
3. start with BayesFlow Base architectures;
4. tune representation dimension before unconstrained depth;
5. use low-fidelity screening at a smaller simulation budget;
6. promote only the best few configurations;
7. use at least three training seeds for finalists;
8. compare total simulator cost, training cost, and deployment cost.

Do not run unrestricted architecture search.

### Expected escalation rules

- poor A likelihood shape but improving with \(d_C\): increase summary dimension;
- poor A despite stable larger summaries: increase ratio-network capacity or simulations;
- good A training loss but poor calibration: diagnose NRE calibration/domain before adding privilege;
- \(A^+\) beats A: privileged information is useful even without a separate privileged latent space;
- B fails but C succeeds: evidence for a Markov-aware inductive-bias advantage;
- C works but D does not: final privileged summary is a better bridge than the high-dimensional sequence;
- D works but E does not improve final likelihood: drop retention regularization;
- good SBI but slow hierarchy: solve deployment compression, not representation learning.

---

# 18. Resource plan

These are planning anchors, not convergence promises.

## 18.1 Simulation banks

For fast benchmark simulators:

- initial shared bank: approximately \(20{,}000\) sittings;
- larger untouched evaluation bank where feasible.

For slower simulators:

- initial pilot: approximately \(3{,}000\)–\(5{,}000\) sittings.

Reuse the same simulations across procedures whenever their required outputs are available.

## 18.2 Storage

For float32 privileged state with dimension \(d_X\),

\[
\text{raw state storage}
\approx
4MTd_X
\text{ bytes}
\]

before observations, masks, metadata, and training activations.

Measure actual sCOIN state size before committing to large simulation banks.

## 18.3 Training runs

Do not run all A-E procedures automatically.

Expected sequence:

1. A, plus NPE cross-check;
2. \(A^+\) only if scientifically useful or A is inadequate;
3. B/C only if privilege remains motivated;
4. D/E only after B/C justify a separate privileged bridge.

Three-seed replication is reserved for finalists rather than every screening configuration.

## 18.4 Labor

Assuming a correct simulator and usable reference implementation, a reasonable planning envelope from the reviews is:

- standard BayesFlow ratio + backend integration + benchmark pilot: roughly 2–4 engineer-weeks;
- full privileged B-E research prototype: roughly 2–4 engineer-months.

These are planning judgments and should be replaced by measured effort after Benchmark 0/1.

---

# 19. Interpretation of the competing claims

The revised project tests the following claims separately.

## Claim A — standard SBI suffices

\[
(Y,U)\rightarrow C^Y\rightarrow\widehat r_Y
\]

is accurate and efficient enough.

This is the null/default engineering hypothesis.

## Claim \(A^+\) — privileged supervision helps without a privileged latent space

Simulator state improves the observed encoder during training but is unnecessary at deployment.

## Claim B — explicit privileged representation helps

A generic

\[
(X,Y,U)\rightarrow C^P
\]

teacher plus an observed bridge improves inference relative to A/\(A^+\).

## Claim C — Markov-aware local encoding helps

The structure

\[
a_t\rightarrow r_t\rightarrow s_t
\]

makes privileged learning more simulation-efficient or robust than giving raw privileged sequences to a generic BayesFlow summary.

## Claim D — the temporally resolved privileged bridge helps

It is better to infer

\[
q(\mathbf s\mid Y,U)
\]

than to infer the final privileged summary

\[
q(C^P\mid Y,U).
\]

## Claim E — retaining privileged state information helps

An explicit state-retention auxiliary loss improves the final observed likelihood, not merely an internal reconstruction metric.

These claims are nested but not logically equivalent. In particular:

- B failing does not prove privileged information is useless;
- C succeeding after B fails supports an inductive-bias interpretation;
- D/E are not prerequisites for C;
- none of B-E is required if A already satisfies the product requirements.

---

# 20. Risks that remain after revision

## 20.1 Ratio calibration

NRE removes posterior/prior division but not approximation error. Contrastive coverage, tails, and calibration remain critical.

## 20.2 Summary sufficiency

A fixed-dimensional \(C^Y\) or \(C^P\) may discard likelihood-relevant information. This is an empirical property, not guaranteed by BayesFlow.

## 20.3 Privileged bridge geometry

Conditional distributions such as

\[
p(\mathbf s\mid Y,U)
\]

may be singular, high-dimensional, multimodal, or strongly constrained. Procedure D is therefore gated by explicit support analysis.

## 20.4 Hierarchy-scale error accumulation

Small systematic sitting-level log-ratio errors can accumulate as the number of sittings grows. Full hierarchical simulation tests are mandatory.

## 20.5 Training-domain mismatch

A new hierarchy can emphasize regions weakly covered by \(\pi_0\) even when it remains formally inside the support.

## 20.6 Simulator contract

Privileged Markov-aware inference is only as valid as the exposed state and scientific simulator implementation.

## 20.7 Consumer integration

A scientifically good ratio estimator can still be unusable if its exported/JAX implementation has incorrect transforms, gradients, dtypes, or column ordering. Integration parity tests are mandatory.

---

# 21. Current decision points

The following remain intentionally unresolved.

| Decision | Current first choice | Escalation / alternative |
|---|---|---|
| observed sequence summary | BayesFlow `TimeSeriesTransformer` | `FusionTransformer`; `TimeSeriesNetwork` |
| likelihood surrogate | BayesFlow NRE-C `RatioApproximator` | NPE + prior division as cross-check; other NRE variants only if diagnosed |
| consumer | HSSM integration spike | direct PyMC if simpler/more flexible |
| privileged generic summary | same BayesFlow time-series summary family | model-specific serializer / FusionNetwork |
| Markov local encoder | shared residual MLP \(a\to r\to s\) | typed branches / set encoder for structured state |
| bridge at B/C | fixed \(C^P\) | Procedure D only if needed |
| \(q(C^P\mid Y,U)\) | conditional Gaussian/GMM | conditional flow |
| \(q(\mathbf s\mid Y,U)\) | only after support analysis; autoregressive GMM/flow | explicit reduced stochastic coordinates |
| integration | fixed Monte Carlo | scrambled QMC if empirically superior |
| sCOIN state representation | fixed bounded slots + masks | alternative only if named simulator requires it |

---

# 22. Minimal algorithmic summary

## Baseline

\[
(\theta,U)
\rightarrow
Y
\]

\[
(Y,U)
\xrightarrow{\text{BayesFlow sequence summary}}
C^Y
\]

\[
(\theta,C^Y)
\xrightarrow{\text{NRE-C}}
\widehat{\log r}_A(\theta;Y,U)
\]

\[
\widehat{\log r}_A
\longrightarrow
\text{HSSM or PyMC hierarchy}.
\]

## Optional privileged teacher

\[
(\theta,U)
\rightarrow
(X,Y)
\]

\[
(X,Y,U)
\xrightarrow{\text{generic BayesFlow summary}}
C^P
\]

or, if justified,

\[
(X,Y,U)
\rightarrow
a_t
\rightarrow
r_t
\rightarrow
s_t
\rightarrow
\text{BayesFlow summary}
\rightarrow
C^P.
\]

Observed bridge:

\[
(Y,U)
\rightarrow
q(C^P\mid Y,U)
\]

or, only if justified,

\[
(Y,U)
\rightarrow
q(\mathbf s\mid Y,U).
\]

Marginalized privileged ratio:

\[
\widehat r(\theta;Y,U)
=
E_{\text{bridge}\mid Y,U}
[
\widehat r_P(\theta;\text{privileged summary})
].
\]

Every extra component survives only if it improves the final likelihood or its simulation/computational efficiency.

---

# 23. What the next review should decide

The next review should focus on the revised design rather than the abandoned assumption that privileged machinery is necessary.

The principal questions are now:

1. Is observed-only BayesFlow NRE a technically sound load-bearing baseline for the declared \(U\perp\theta\) scope?
2. Is the HSSM sitting-as-row integration plausible enough to justify an integration spike, or should PyMC be the default consumer?
3. Does Procedure \(A^+\) adequately test the cheapest use of privileged state?
4. Is Procedure B's compressed-privileged marginalization mathematically specified clearly enough, including its sufficiency approximation?
5. Does Procedure C isolate a meaningful Markov-aware inductive bias without reintroducing unnecessary architecture?
6. Is Procedure D's reference-measure gate sufficient to prevent invalid full-dimensional densities on singular bridge distributions?
7. Is E now framed safely as auxiliary retention rather than a falsely exact backward density?
8. Are the validation gates stringent enough to detect hierarchy-scale surrogate error?
9. Is bounded sCOIN scoped precisely enough to be a legitimate third benchmark?
10. Are the stopping rules strong enough to prevent unnecessary privileged-system development?

---

# References and implementation sources

1. Cranmer K, Brehmer J, Louppe G. **The frontier of simulation-based inference.** *PNAS*. 2020;117(48):30055–30062.  
   https://doi.org/10.1073/pnas.1912789117

2. Radev ST, Mertens UK, Voss A, Ardizzone L, Köthe U. **BayesFlow: Learning Complex Stochastic Models With Invertible Neural Networks.** *IEEE TNNLS*. 2022;33(4):1452–1466.  
   https://doi.org/10.1109/TNNLS.2020.3042395

3. Miller BK, Weniger C, Forré P. **Contrastive Neural Ratio Estimation for Simulation-based Inference.** *NeurIPS*. 2022.  
   https://arxiv.org/abs/2210.06170

4. BayesFlow documentation. **RatioApproximator / NRE-C.**  
   https://bayesflow.org/v2.0.13/api/bayesflow.approximators.RatioApproximator.html

5. BayesFlow documentation. **Summary Networks; TimeSeriesTransformer.**  
   https://bayesflow.org/v2.0.12/user_guide/summary_networks.html  
   https://bayesflow.org/v2.0.14/api/bayesflow.networks.summary.TimeSeriesTransformer.html

6. HSSM documentation. **Integrate a BayesFlow NRE (ONNX).**  
   https://lnccbrown.github.io/HSSM/tutorials/bayesflow_nre_onnx_integration/

7. HSSM documentation. **The ONNX likelihood contract.**  
   https://lnccbrown.github.io/HSSM/how_to/custom_onnx_likelihoods/

8. HSSM documentation. **Likelihood kinds / custom JAX likelihoods.**  
   https://lnccbrown.github.io/HSSM/explanations/likelihoods/  
   https://lnccbrown.github.io/HSSM/tutorials/jax_callable_contribution_onnx_example/

9. Heald JB, Lengyel M, Wolpert DM. **Contextual inference underlies the learning of sensorimotor repertoires.** *Nature*. 2021;600:489–493.  
   https://doi.org/10.1038/s41586-021-04129-3

10. Cuevas Rivera D, Kiebel SJ. **The effects of probabilistic context inference on motor adaptation.** *PLOS ONE*. 2023.  
    https://doi.org/10.1371/journal.pone.0286749

11. Lueckmann J-M, Boelts J, Greenberg D, Gonçalves PJ, Macke JH. **Benchmarking Simulation-Based Inference.** *AISTATS / PMLR*. 2021;130:343–351.  
    https://proceedings.mlr.press/v130/lueckmann21a.html

12. Talts S, Betancourt M, Simpson D, Vehtari A, Gelman A. **Validating Bayesian Inference Algorithms with Simulation-Based Calibration.** 2018.  
    https://arxiv.org/abs/1804.06788

13. Modrák M, Moon AH, Kim S, Bürkner P-C, Huurre N, Faltejsková K, Gelman A, Vehtari A. **Simulation-based calibration checking for Bayesian computation: the choice of test quantities shapes sensitivity.** *Bayesian Analysis*.  
    https://paulbuerkner.com/publications/pdf/2023__Modrak_et_al__Bayesian_Analysis.pdf

14. Dirmeier S, Albert C, Perez-Cruz F. **Simulation-based Inference for High-dimensional Data using Surjective Sequential Neural Likelihood Estimation.** *UAI / PMLR*. 2025;286:1039–1063.  
    https://proceedings.mlr.press/v286/dirmeier25a.html

15. Tsampourakis K, Elvira V. **Truncated Neural Likelihood Estimation for Simulation-Based Inference in State-Space Models.** 2026 preprint.  
    https://arxiv.org/abs/2605.21805

16. Vapnik V, Vashist A. **A new learning paradigm: Learning using privileged information.** *Neural Networks*. 2009.  
    https://www.sciencedirect.com/science/article/pii/S0893608009001130

17. Brehmer J, Cranmer K, Louppe G, Pavez J. **Mining gold from implicit models to improve likelihood-free inference.** 2018.  
    https://arxiv.org/abs/1805.12244

18. Owen AB. **Scrambling Sobol' and Niederreiter–Xing Points.** *Journal of Complexity*. 1998;14(4):466–489.  
    https://doi.org/10.1006/jcom.1998.0487

19. Abril-Pla O, Andreani V, Carroll C, et al. **PyMC: a modern and comprehensive probabilistic programming framework in Python.** *PeerJ Computer Science*. 2023;9:e1516.  
    https://doi.org/10.7717/peerj-cs.1516
