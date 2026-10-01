# 0003 — Keras on the JAX backend

**Date:** 2026-09-30 · **Status:** Accepted

**Context:** BayesFlow 2 runs on Keras 3, which can use JAX, PyTorch or TensorFlow. HSSM
and PyMC can use JAX for likelihoods and sampling. A later goal is to use a BayesFlow
learned likelihood inside HSSM.

**Decision:** Keras uses the JAX backend (`KERAS_BACKEND=jax`, set by the pixi
environment).

**Why:** One numerical backend across BayesFlow training and the HSSM/PyMC consumer makes
handing a learned likelihood over as a JAX function possible, and JAX is the backend the
BayesFlow skill and documentation default to. *Alternatives:* PyTorch (no natural route
into PyMC/HSSM), TensorFlow (declining support).

**Consequences:** BayesFlow ≥ 2.0.13 and HSSM 0.5.0 currently need incompatible numpy
versions (#4); the HSSM work will need either two environments or BayesFlow ≤ 2.0.12.
PyMC's default multiprocess sampling warns about forking after JAX is imported; notebook
sampling setup is still to be decided (`cores=1` or nutpie).
