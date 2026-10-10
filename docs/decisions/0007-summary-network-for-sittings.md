# 0007 — Summary network for Sittings: convolution and recurrence, full length, with a real-Trial flag

**Date:** 2026-10-10 · **Status:** Proposed

**Context:** a BayesFlow posterior network needs a summary network that turns a Sitting
(one row per Trial, about 200 to over 2,000 Trials) into a short vector. BayesFlow offers
several, and they differ in how their cost grows with Sitting length, in what they are
predisposed to learn, and in how they treat the padding that brings Sittings to a common
length. Background, in plain words:
[Concept-summary-networks](https://github.com/opherdonchin/MotorAdpatationSBI/wiki/Concept-summary-networks).
The choice does not change the code around the network, but it decides training time,
the longest Sitting we can handle on a given computer, and whether padding can affect a
posterior. Constraint (Opher, 2026-10-06): no downsampling of Sittings.

**Decision:** for the one-state Model's posterior network (step C3b of
[issue #12](https://github.com/opherdonchin/MotorAdpatationSBI/issues/12)), and as the
starting point for later Models:

1. The summary network is BayesFlow's `TimeSeriesNetwork` (two convolution layers, then
   recurrent layers reading every Trial in both directions), at BayesFlow's "Base" size.
2. Sittings are read at full length. No downsampling, no strides, no truncation.
3. Sittings are padded with zeros to the longest Sitting of the training Experiment.
   Because `TimeSeriesNetwork` takes no padding mask, each Trial carries a fourth input,
   `real`: 1 on a real Trial, 0 on padding.
4. A Sitting is given to the trained Inference Engine padded to the same length as in
   training. A longer Sitting is outside what the Engine was trained for.

**Why:**

- *Cost.* A transformer's memory grows with the square of the Sitting length; on our
  8 GB graphics card only 4 full-length Sittings fit in a batch, and training on 20,000
  Sittings for 100 epochs would take about 8 hours. The recurrent networks grow in
  proportion to length: 32 Sittings per batch, about 3 hours.
- *Fit to the Models.* Our Models are recursions over Trials, and their exact likelihoods
  are computed by recursions (a Kalman filter). A network that reads Trials in order and
  carries a state is predisposed to the right kind of quantity.
- *It learns.* On the 2,000-Sitting demo Experiment (1,700 for training, 40 epochs;
  one-off probes, [journal 2026-10-10](../journal/2026-10-10.md)) it reached a
  validation loss of about 0.8 and posterior contractions of 0.48 ($A$), 0.68 ($B$),
  0.82 ($\sigma_\eta$) and 0.97 ($\sigma_\varepsilon$), with calibration errors of 0.03
  to 0.04.

Alternatives considered:

- *`TimeSeriesTransformer`, `FusionTransformer`.* Handle padding exactly, with a mask.
  Rejected for now on cost alone; worth a comparison on a stronger computer.
- *`RecurrentNetwork` with its padding mask.* On paper the best of both: cost in
  proportion to length, and a padded Trial leaves its state exactly unchanged (confirmed:
  overwriting the padding changed the summary by exactly 0). In the same probe it did not
  learn: validation loss stayed near 1.5 and contraction near 0 for all four parameters.
  One suspected cause, the raw Trial number (up to 2,265) fed to the recurrent layers by
  its position encoding, was tested by supplying Trial numbers divided by 1,000; the
  validation loss improved only to about 1.3. The cause is not known. Set aside, not
  ruled out.
- *Downsampling, or shorter Sittings.* Not needed: full-length Sittings fit.

**Consequences:**

- Padding is not guaranteed to be harmless. The network must learn from `real` to carry
  its state through the padding, and every Engine trained this way needs a Check of how
  much its summaries depend on padding.
- An Engine is tied to its padded length; that length is saved in the Engine's record.
- Sitting length is confounded with the amount of padding during training. This is
  harmless as long as point 4 is respected.
- This is a choice within the standard method, in which a whole Sitting is summarized at
  once. Using the Models' Trial-by-Trial structure more strongly (a network for the
  one-Trial likelihood) would remove padding and Sitting length from the problem; that is
  a separate line of work, not decided here.
