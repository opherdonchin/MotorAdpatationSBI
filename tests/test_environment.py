"""Environment smoke tests: the pixi environment imports, uses the GPU, and can run
a minimal PyMC fit and a minimal BayesFlow training round trip.

These check the installation, not any scientific result.
"""

import os

import numpy as np
import pytest

ROOT_SEED = 0x5EED_E4B1_7A3C_91D2_6F08_C4A5_B3E7_1D29


@pytest.fixture
def rng():
    return np.random.default_rng(ROOT_SEED)


def test_keras_uses_jax_backend():
    import keras

    assert os.environ.get("KERAS_BACKEND") == "jax"
    assert keras.backend.backend() == "jax"


def test_jax_sees_gpu():
    import jax

    assert jax.default_backend() == "gpu", jax.devices()


def test_project_packages_import():
    import motor_sbi  # noqa: F401
    import simulators  # noqa: F401


def test_pymc_recovers_normal_mean(rng):
    import pymc as pm

    true_mu = 1.5
    y = rng.normal(true_mu, 1.0, size=200)

    with pm.Model():
        mu = pm.Normal("mu", 0.0, 10.0)
        pm.Normal("y", mu, 1.0, observed=y)
        idata = pm.sample(
            draws=500,
            tune=500,
            chains=2,
            cores=1,  # multiprocess fork after JAX import can deadlock
            random_seed=rng,
            progressbar=False,
        )

    post_mean = float(idata.posterior["mu"].mean())
    assert abs(post_mean - true_mu) < 0.3


def test_bayesflow_train_and_sample_round_trip(rng):
    import bayesflow as bf
    import keras

    stream_sim, stream_keras = rng.spawn(2)
    keras.utils.set_random_seed(int(stream_keras.integers(2**31)))

    # Simulator functions close over their Generator; make_simulator infers
    # inputs from the function signature, so functools.partial is not accepted.
    def prior():
        return {"mu": stream_sim.normal(0.0, 1.0)}

    def observation_model(mu):
        return {"x": stream_sim.normal(mu, 0.5, size=2)}

    simulator = bf.make_simulator([prior, observation_model])
    adapter = (
        bf.Adapter()
        .convert_dtype("float64", "float32")
        .concatenate(["mu"], into="inference_variables")
        .concatenate(["x"], into="inference_conditions")
    )
    workflow = bf.BasicWorkflow(
        simulator=simulator,
        adapter=adapter,
        # FlowMatching, not CouplingFlow: a coupling flow on a single parameter
        # leaves half its layers unused and Keras then refuses to build it.
        inference_network=bf.networks.FlowMatching(),
    )

    train = workflow.simulate(512)
    val = workflow.simulate(64)
    history = workflow.fit_offline(
        data=train, epochs=2, batch_size=64, validation_data=val, verbose=0
    )
    assert np.all(np.isfinite(history.history["loss"]))

    samples = workflow.sample(conditions={"x": np.array([[0.3, 0.4]])}, num_samples=50)
    assert samples["mu"].shape[:2] == (1, 50)
    assert np.all(np.isfinite(samples["mu"]))
