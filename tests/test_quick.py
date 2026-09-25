"""Fast, data-free checks for the observation-system research script.

The module is loaded with the FMM-worker flag so the optional Devito stack is
not imported.  The scientific main workflow is protected by its __main__ guard
and is therefore not started by these tests.
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys
import unittest

import numpy as np


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    REPOSITORY_ROOT / "Final_observation_system_adaptive_2D_3D_complete.py"
)

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ["ROBUST_FMM_PROCESS_WORKER"] = "1"

SPEC = importlib.util.spec_from_file_location("adaptive_observation_system", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load module from {MODULE_PATH}")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class QuickTest(unittest.TestCase):
    def test_expected_entry_points_exist(self):
        self.assertTrue(callable(MODULE.main))
        self.assertTrue(callable(MODULE.run_path_correlated_joint_design_validation))
        self.assertTrue(callable(MODULE.run_localization_migration_advantage_evidence))

    def test_small_grid_traveltime_is_finite(self):
        physics = MODULE.PhysicsEngine(
            shape=(9, 7), spacing=(10.0, 10.0), is_3d=False
        )
        source = (4, 3)
        travel_time = physics.compute_traveltime_field(source)

        self.assertEqual(travel_time.shape, physics.shape)
        self.assertTrue(np.all(np.isfinite(travel_time)))
        # scikit-fmm places the zero level set between cells, so the source-cell
        # time can be a small positive number rather than exactly zero.
        self.assertEqual(
            np.unravel_index(int(np.argmin(travel_time)), travel_time.shape),
            source,
        )
        self.assertLess(float(travel_time[source]), float(travel_time[0, 0]))
        self.assertGreater(float(travel_time[0, 0]), 0.0)

    def test_correlated_noise_covariance_is_positive_definite(self):
        physics = MODULE.PhysicsEngine(
            shape=(9, 7), spacing=(10.0, 10.0), is_3d=False
        )
        sensors = [(0, 0), (4, 0), (8, 0)]
        noise = MODULE.OperationalNoiseModel(
            "quick-test", sigma=0.002, correlation_length_m=25.0
        )
        covariance = noise.covariance(physics, sensors)
        factor = MODULE._stable_cholesky(covariance)

        self.assertEqual(covariance.shape, (3, 3))
        self.assertTrue(np.all(np.linalg.eigvalsh(covariance) > 0.0))
        np.testing.assert_allclose(
            factor @ factor.T, covariance, rtol=1.0e-10, atol=1.0e-14
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
