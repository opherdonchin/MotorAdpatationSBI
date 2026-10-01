# 0001 — pixi with conda-forge for the environment

**Date:** 2026-09-30 · **Status:** Accepted

**Context:** The stack combines PyMC/PyTensor (which compiles C code and needs a compiler
and BLAS), JAX with CUDA, Keras, BayesFlow and later HSSM. The system Python (3.14) is too
new for parts of this stack.

**Decision:** Use pixi with the manifest in `pyproject.toml`, Python 3.12, conda-forge for
every package available there, and PyPI only for packages that are not (BayesFlow). JAX's
CUDA build comes from conda-forge, declared through a CUDA 12 platform entry.

**Why:** conda-forge is the channel PyMC and PyTensor recommend; it supplies the compiler
and BLAS that otherwise make PyTensor slow or fragile. pixi adds a lockfile and named
tasks, and reading `pyproject.toml` keeps the repo a normal Python package.
*Alternative:* uv — faster and more familiar to Python users, but it leaves PyTensor
relying on system compilers and BLAS outside the lockfile.

**Consequences:** Collaborators need pixi. Fast-moving packages are pinned to a minor
version in the manifest and updated deliberately; the lockfile pins everything exactly.
Mixing conda and PyPI packages can occasionally complicate solving.
