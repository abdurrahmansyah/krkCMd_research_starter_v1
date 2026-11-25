"""
tests/test_resource_policy.py

Unit tests for dynamic resource safety policy and process monitoring (M01.1 Section O).
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from resource_policy import (  # noqa: E402
    build_thread_env,
    compute_dynamic_budgets,
    run_monitored_subprocess,
)


class TestResourcePolicy(unittest.TestCase):
    def test_ram_budget_capped_at_64gb_when_ram_abundant(self) -> None:
        # With ~116 GB available, 0.70*116 = 81.2 and 116-16 = 100, so cap 64 GB must apply!
        b = compute_dynamic_budgets(available_ram_gb=116.0, available_vram_gb=23.7, available_disk_gb=1877.0, logical_cores=20)
        self.assertEqual(b.ram_budget_gb, 64.0)
        self.assertEqual(b.vram_budget_gb, 20.0)
        self.assertEqual(b.initial_env_cache_budget_gb, 30.0)
        self.assertEqual(b.default_cpu_threads, 16)

    def test_low_resource_floor_clamps_to_zero(self) -> None:
        b = compute_dynamic_budgets(available_ram_gb=10.0, available_vram_gb=2.0, available_disk_gb=80.0, logical_cores=8)
        self.assertEqual(b.ram_budget_gb, 0.0)
        self.assertEqual(b.vram_budget_gb, 0.0)
        self.assertEqual(b.initial_env_cache_budget_gb, 0.0)
        self.assertEqual(b.default_cpu_threads, 4)

    def test_intermediate_budgets(self) -> None:
        b = compute_dynamic_budgets(available_ram_gb=50.0, available_vram_gb=12.0, available_disk_gb=115.0, logical_cores=20)
        self.assertAlmostEqual(b.ram_budget_gb, 34.0)  # min(64, 35.0, 34.0)
        self.assertAlmostEqual(b.vram_budget_gb, 9.5)  # min(20, 10.2, 9.5)
        self.assertAlmostEqual(b.initial_env_cache_budget_gb, 15.0)

    def test_thread_env_controls(self) -> None:
        env = build_thread_env(cpu_threads=16, base_env={})
        for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
            self.assertEqual(env[key], "16")

    def test_monitored_subprocess_timeout_terminates_tree(self) -> None:
        res = run_monitored_subprocess(
            [sys.executable, "-c", "import time; time.sleep(10)"],
            timeout_sec=1,
            cpu_threads=4,
            poll_interval_sec=0.1,
        )
        self.assertTrue(res["timed_out"])
        self.assertEqual(res["returncode"], -1)
        self.assertGreaterEqual(res["peak_rss_mb"], 0.0)


if __name__ == "__main__":
    unittest.main()
