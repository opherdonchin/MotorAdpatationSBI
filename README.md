# MotorAdpatationSBI

Use SBI techniques including HSSM and dimensionality reduction like BayesFlow to do
identification using models of motor adaptation.

## Setup

Requires [pixi](https://pixi.sh) and an NVIDIA GPU whose driver supports CUDA 12 or later.

```bash
pixi install        # build the environment from pixi.lock
pixi run test       # environment smoke tests
pixi run lab        # JupyterLab
```

Keras runs on the JAX backend (`KERAS_BACKEND=jax` is set by the environment).

Contributors (human or AI) should read [AGENTS.md](AGENTS.md) first.
