"""
tests/test_m03_metrics_perturbations_watchdog.py

Synthetic validation tests for M03:
  - Predictive accuracy, measurement agreement, engineering tolerance, robustness metrics
  - Deterministic perturbations & [0, 255] clipping & shape preservation
  - Watchdog simulated suspend/resume clock jump detection & timeout enforcement
  - Experiment runner real-data authorization guard
"""

import sys
import tempfile
import unittest
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from resource_policy import run_monitored_subprocess  # noqa: E402
from src.evaluation.experiment_runner import ExperimentSpec, execute_experiment  # noqa: E402
from src.evaluation.metrics import (  # noqa: E402
    compute_engineering_tolerances,
    compute_measurement_agreement,
    compute_predictive_accuracy,
    compute_robustness_summary,
)
from src.features.perturbations import (  # noqa: E402
    apply_brightness_shift,
    apply_combined_corruption,
    apply_contrast_scale,
    apply_downsample_interp,
    apply_gamma,
    apply_gaussian_noise,
    apply_gaussian_smoothing,
    apply_illumination_gradient,
    apply_impulse_noise,
)


class TestM03MetricsPerturbationsAndWatchdog(unittest.TestCase):
    def test_predictive_accuracy_and_zero_wape_guard(self) -> None:
        yt = np.array([0.0, 50.0, 100.0, 150.0])
        yp = np.array([2.0, 55.0, 95.0, 160.0])
        m = compute_predictive_accuracy(yt, yp)
        self.assertAlmostEqual(m["mae_um"], 5.5)
        self.assertGreater(m["r2"], 0.98)
        m_zero = compute_predictive_accuracy(np.zeros(4), np.ones(4))
        self.assertIsNone(m_zero["wape"])

    def test_agreement_tolerances_and_robustness_metrics(self) -> None:
        yt = np.linspace(20.0, 200.0, 20)
        yp = yt + np.linspace(-4.0, 4.0, 20)
        ag = compute_measurement_agreement(yt, yp)
        self.assertGreater(ag["lins_ccc"], 0.99)
        tol = compute_engineering_tolerances(yt, yp)
        self.assertEqual(tol["within_5um_rate"], 1.0)
        rob = compute_robustness_summary(
            yt, yp, {"s1": yp + 5.0, "s2": yp + 15.0}, severities=[1.0, 2.0]
        )
        self.assertGreater(rob["mean_corrupted_mae_um"], rob["clean_mae_um"])
        self.assertIsNotNone(rob["area_under_severity_error_curve"])

    def test_all_perturbations_preserve_shape_and_clip_255(self) -> None:
        rng = np.random.default_rng(42)
        X = rng.uniform(10.0, 245.0, size=(8, 501)).astype(np.float32)
        outs = [
            apply_brightness_shift(X, -30),
            apply_contrast_scale(X, 1.3),
            apply_gaussian_noise(X, 10.0, seed=42),
            apply_gaussian_smoothing(X, 1.0),
            apply_gamma(X, 1.2),
            apply_illumination_gradient(X, 25.0),
            apply_impulse_noise(X, 0.02, seed=42),
            apply_downsample_interp(X, 4),
            apply_combined_corruption(X, seed=42),
        ]
        for out in outs:
            self.assertEqual(out.shape, (8, 501))
            self.assertTrue(np.isfinite(out).all())
            self.assertGreaterEqual(float(out.min()), 0.0)
            self.assertLessEqual(float(out.max()), 255.0)

    def test_watchdog_detects_simulated_suspend_clock_jump(self) -> None:
        ticks = iter([0.0, 0.1, 500.0, 500.1])  # simulated 500s suspend jump!
        res = run_monitored_subprocess(
            [sys.executable, "-c", "import time; time.sleep(5)"],
            timeout_sec=10,
            poll_interval_sec=0.05,
            clock_fn=lambda: next(ticks, 500.2),
            suspend_gap_threshold_sec=30.0,
        )
        self.assertTrue(res["timed_out"])
        self.assertTrue(res["suspend_detected"])
        self.assertIn("SUSPEND_DETECTED", res["violation_reason"])
        self.assertEqual(res["returncode"], -1)

    def test_experiment_runner_blocks_unauthorized_real_data_training(self) -> None:
        spec = ExperimentSpec(
            model_id="ML04",
            config_id="default",
            run_id="M03_TEST",
            attempt_id="ATT_01",
            split_manifest="reports/tables/group_split_manifest.csv",
            seed=42,
            environment_executable=sys.executable,
            worker_module="src.evaluation.m02a_compat_worker",
            authorize_real_data_training=False,
        )
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(PermissionError):
                execute_experiment(spec, Path(tmp))


if __name__ == "__main__":
    unittest.main()
