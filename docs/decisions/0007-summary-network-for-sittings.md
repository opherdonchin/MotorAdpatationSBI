# 0007 — Reading Sittings: a convolution and recurrence summary network, full length, one Schedule per batch

**Date:** 2026-10-10 · **Status:** Proposed

**Context:** a BayesFlow posterior network needs a summary network that turns a Sitting
(one row per Trial, about 200 to over 2,000 Trials) into a short vector. BayesFlow offers
several, and they differ in how their cost grows with Sitting length and in what they are
predisposed to learn. A trained summary network takes a Sitting of any length; what must
be equal is the length of the Sittings *within one training batch*, because a batch is
one array. There are two ways to arrange that: pad every Sitting to a common length, or
make the Sittings of a batch equally long to begin with. Background, in plain words:
[Concept-summary-networks](https://github.com/opherdonchin/MotorAdpatationSBI/wiki/Concept-summary-networks).
Constraint (Opher, 2026-10-06): no downsampling of Sittings.

**Decision:** for the one-state Model's posterior network (step C3b of
[issue #12](https://github.com/opherdonchin/MotorAdpatationSBI/issues/12)), and as the
starting point for later Models:

1. The summary network is BayesFlow's `TimeSeriesNetwork` (two convolution layers, then
   recurrent layers reading every Trial in both directions), at BayesFlow's "Base" size.
2. Sittings are read at full length. No downsampling, no strides.
3. No padding. All Sittings in a training batch are done on one Schedule, so they have
   one length; each batch has its own Schedule. This is a way of running the Simulator,
   not a change to the Model, the Prior or the Schedule Design.
4. Training Sittings are simulated as they are needed, batch by batch, and not reused.
5. The Schedule of a training batch is cut down to a multiple of 25 Trials. This is for
   speed only: JAX compiles the training step again for every new length.

**Why:**

- *Cost.* A transformer's memory grows with the square of the Sitting length; on our
  8 GB graphics card only 4 full-length Sittings fit in a batch. The recurrent networks
  grow in proportion to length.
- *Fit to the Models.* Our Models are recursions over Trials, and their exact likelihoods
  are computed by recursions (a Kalman filter). A network that reads Trials in order and
  carries a state is predisposed to the right kind of quantity.
- *It learns.* In a small probe with padded Sittings (1,700 for training, 40 epochs;
  [journal 2026-10-10](../journal/2026-10-10.md)) it reached posterior contractions of
  0.48 ($A$), 0.68 ($B$), 0.82 ($\sigma_\eta$) and 0.97 ($\sigma_\varepsilon$), with
  calibration errors of 0.03 to 0.04.
- *No padding* (Opher, 2026-10-10). `TimeSeriesNetwork` cannot be told to skip padded
  Trials; with padding it would have to learn to carry its state through them, the
  trained Engine would be tied to its padded length, and nearly two thirds of the
  training array would be padding. With one Schedule per batch none of this arises, and
  the Engine takes any Sitting as it is. The price is small: Sittings within a batch are
  alike in their Schedule, which makes each batch a slightly less varied sample.

Alternatives considered:

- *Padding to the longest Sitting, with a mask or a flag.* Tried first; see above.
- *`TimeSeriesTransformer`, `FusionTransformer`.* Rejected for now on cost alone; worth a
  comparison on a stronger computer.
- *`RecurrentNetwork`.* Recurrent, and it takes a padding mask, under which a padded
  Trial leaves its state exactly unchanged (confirmed). In the padded probe it did not
  learn: validation loss stayed near 1.5, against 0.8, and contraction near 0 for all
  four parameters. Giving it Trial numbers divided by 1,000, in case its position
  encoding was the trouble, improved the loss only to about 1.3. The cause is not known.
  Set aside, not ruled out.
- *Training from a saved Experiment in which every Sitting has its own Schedule,* as
  first agreed. That forces padding, or batching code of our own.
- *Downsampling, or shorter Sittings.* Not needed.

**Consequences:**

- `simulate_experiment` can put several Sittings on one Schedule
  (`n_sittings_per_schedule`).
- Training data are not saved. They are regenerable from the notebook's seed; the test
  Experiment used for the Checks is saved.
- The loss after each epoch is computed on held-out Sittings that share one Schedule, so
  its level depends on that Schedule; its trend is what shows convergence.
- A new Sitting length costs a few seconds of compilation, in training and in use.
  Hence point 5 in training. Test Sittings are not cut, so the Checks also show whether
  the Engine handles lengths it never trained on.
- This is a choice within the standard method, in which a whole Sitting is summarized at
  once. Using the Models' Trial-by-Trial structure more strongly (a network for the
  one-Trial likelihood) is a separate line of work, not decided here.
