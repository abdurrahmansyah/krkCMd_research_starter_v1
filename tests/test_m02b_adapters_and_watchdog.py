"""
tests/test_m02b_adapters_and_watchdog.py

Targeted unit tests for M02B Section 11:
  - Registry-driven candidate resolution & runtime evidence reconciliation
  - Resource-budget violation detection & simulated RAM reserve breach
  - Safe stdout/stderr log-file handling (no pipe deadlock on large output)
  - M02B adapter identities, DL01/RF05 separation, invalid outputs
"""

import sys
import unittest
from pathlib import Path
import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from build_compatibility_matrix import load_registry_candidates, reconcile_effective_matrix  # noqa: E402
from resource_policy import BYTES_PER_GIB, check_resource_limits, run_monitored_subprocess  # noqa: E402
from src.models.m02a_adapters import validate_predictions, validate_tabular_inputs  # noqa: E402
from src.models.m02b_adapters import ADAPTER_REGISTRY_M02B, get_m02b_adapter  # noqa: E402


class TestM02BWatchdogAndRegistry(unittest.TestCase):
    def test_registry_driven_loading_has_32_candidates(self) -> None:
        cands = load_registry_candidates(ROOT / "configs" / "model_registry.yaml")
        self.assertEqual(len(cands), 32)
        self.assertEqual(len({c["id"] for c in cands}), 32)

    def test_reconcile_never_marks_approved_and_preserves_m02a(self) -> None:
        m02a_dir = ROOT / "reports" / "runs" / "M02A_20261125_074616_DESKTOP-CQB09OU"
        rows = reconcile_effective_matrix(
            ROOT / "configs" / "model_registry.yaml",
            m01_1_matrix_path=ROOT / "reports" / "tables" / "model_compatibility_matrix_M01_1.csv",
            m02a_run_dir=m02a_dir,
        )
        self.assertEqual(len(rows), 32)
        by_id = {r["id"]: r for r in rows}
        self.assertEqual(by_id["ML04"]["effective_runtime_status"], "SCALE_CHECK_PASS")
        self.assertEqual(by_id["SG06"]["effective_runtime_status"], "BLOCKED")
        for r in rows:
            self.assertEqual(r["experimental_approval"], "NOT_APPROVED")

    def test_resource_limit_checker_catches_ram_and_vram_violations(self) -> None:
        # Process RSS > budget
        v1 = check_resource_limits(
            proc_rss_bytes=70 * BYTES_PER_GIB,
            sys_avail_ram_bytes=50 * BYTES_PER_GIB,
            ram_budget_bytes=64 * BYTES_PER_GIB,
            ram_reserve_bytes=16 * BYTES_PER_GIB,
        )
        self.assertIn("PROCESS_RAM_BUDGET_EXCEEDED", v1)

        # System RAM reserve breached
        v2 = check_resource_limits(
            proc_rss_bytes=1 * BYTES_PER_GIB,
            sys_avail_ram_bytes=10 * BYTES_PER_GIB,
            ram_budget_bytes=64 * BYTES_PER_GIB,
            ram_reserve_bytes=16 * BYTES_PER_GIB,
        )
        self.assertIn("SYSTEM_RAM_RESERVE_BREACHED", v2)

        # GPU VRAM reserve breached
        v3 = check_resource_limits(
            proc_rss_bytes=1 * BYTES_PER_GIB,
            sys_avail_ram_bytes=50 * BYTES_PER_GIB,
            ram_budget_bytes=64 * BYTES_PER_GIB,
            ram_reserve_bytes=16 * BYTES_PER_GIB,
            gpu_used_delta_bytes=1 * BYTES_PER_GIB,
            sys_free_vram_bytes=1 * BYTES_PER_GIB,
            vram_budget_bytes=20 * BYTES_PER_GIB,
            vram_reserve_bytes=int(2.5 * BYTES_PER_GIB),
        )
        self.assertIn("GPU_VRAM_RESERVE_BREACHED", v3)

    def test_simulated_ram_reserve_violation_terminates_subprocess(self) -> None:
        res = run_monitored_subprocess(
            [sys.executable, "-c", "import time; time.sleep(10)"],
            timeout_sec=10,
            poll_interval_sec=0.1,
            ram_probe=lambda: 4 * BYTES_PER_GIB,  # simulated low available RAM (< 16 GiB reserve)
        )
        self.assertEqual(res["returncode"], -1)
        self.assertIn("SYSTEM_RAM_RESERVE_BREACHED", res["violation_reason"])

    def test_large_stdout_does_not_deadlock(self) -> None:
        res = run_monitored_subprocess(
            [sys.executable, "-c", "print('X' * 200000)"],
            timeout_sec=10,
            poll_interval_sec=0.1,
        )
        self.assertEqual(res["returncode"], 0)
        self.assertGreaterEqual(len(res["stdout"]), 200000)

    def test_m02b_adapter_identities_and_separations(self) -> None:
        self.assertIn("DL01", ADAPTER_REGISTRY_M02B)
        self.assertIn("RF05", ADAPTER_REGISTRY_M02B)
        dl01 = get_m02b_adapter("DL01")
        self.assertEqual(dl01.expected_module, "torch.nn")
        rf05 = get_m02b_adapter("RF05")
        self.assertEqual(rf05.expected_class, "DLM15LayerCNN_Table3")
        dl05 = get_m02b_adapter("DL05")
        self.assertGreater(dl05.k, 1)  # TabM ensemble size must be > 1
        with self.assertRaises(KeyError):
            get_m02b_adapter("DL04")  # TabR is CONDITIONAL repo-only, not mocked!

    def test_invalid_inputs_and_outputs_rejected(self) -> None:
        with self.assertRaises(ValueError):
            validate_tabular_inputs(np.zeros((4, 500), dtype=np.float32))
        with self.assertRaises(ValueError):
            validate_predictions(np.array([1.0, np.nan]), expected_n=2)
        with self.assertRaises(ValueError):
            validate_predictions(np.array([1.0, np.inf]), expected_n=2)


if __name__ == "__main__":
    unittest.main()
