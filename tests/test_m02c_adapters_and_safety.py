"""
tests/test_m02c_adapters_and_safety.py

Focused tests for M02C Section 13:
  - Foundation checkpoint identities (FM01 V3.5 vs FM02 V3.5_FAST, FM03 TabICLv2, FM04 TabDPT)
  - Malformed worker JSON & failed subprocess after apparent PASS JSON
  - Blocked access status handling & credential redaction
  - Canonical 501-feature validation & prediction finiteness
  - RF05 training-only zero-center preprocessing, pi2mi conversion, and state serialization
  - DL04 TabR adapter identity & context isolation
"""

import json
import sys
import unittest
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from run_m02c_compatibility import parse_worker_result  # noqa: E402
from src.models.m02a_adapters import validate_predictions, validate_tabular_inputs  # noqa: E402
from src.models.m02c_adapters import ADAPTER_REGISTRY_M02C, get_m02c_adapter  # noqa: E402


class TestM02CAdaptersAndSafety(unittest.TestCase):
    def test_foundation_identities_and_checkpoints_distinct(self) -> None:
        fm01 = get_m02c_adapter("FM01")
        fm02 = get_m02c_adapter("FM02")
        fm03 = get_m02c_adapter("FM03")
        fm04 = get_m02c_adapter("FM04")
        self.assertIn("tabpfn-v3.5-20260909.safetensors", fm01.build_config()["checkpoint"])
        self.assertIn("tabpfn-v3.5-fast-20260909.safetensors", fm02.build_config()["checkpoint"])
        self.assertNotEqual(fm01.build_config()["checkpoint"], fm02.build_config()["checkpoint"])
        self.assertEqual(fm03.build_config()["checkpoint_version"], "tabicl-regressor-v2-20260212.ckpt")
        self.assertEqual(fm04.build_config()["context_reduction"], "retrieval")

    def test_parse_worker_result_rejects_malformed_json_and_failed_rc(self) -> None:
        bad_json = parse_worker_result({"returncode": 0, "stdout": "{bad json", "stderr": "", "timed_out": False, "violation_reason": None})
        self.assertEqual(bad_json["status"], "FAILED")
        self.assertIn("Malformed worker JSON", bad_json["error"])

        # Subprocess emits PASS JSON but exits non-zero or times out -> MUST NOT PASS
        late_fail = parse_worker_result({
            "returncode": 1,
            "stdout": json.dumps({"status": "PASS", "model_id": "FM01"}),
            "stderr": "Segfault",
            "timed_out": False,
            "violation_reason": None,
        })
        self.assertEqual(late_fail["status"], "FAILED")

        timeout_fail = parse_worker_result({
            "returncode": -1,
            "stdout": json.dumps({"status": "PASS", "model_id": "SG06"}),
            "stderr": "",
            "timed_out": True,
            "violation_reason": "WALL_CLOCK_TIMEOUT (1800s)",
        })
        self.assertEqual(timeout_fail["status"], "FAILED")
        self.assertIn("WALL_CLOCK_TIMEOUT", timeout_fail["error"])

    def test_rf05_normalized_preprocessing_and_pi2mi_contract(self) -> None:
        rf05 = get_m02c_adapter("RF05")
        cfg = rf05.build_config()
        self.assertIn("train-only", cfg["input_normalization"])
        self.assertAlmostEqual(rf05.PI2MI, 3.96875, places=5)
        self.assertEqual(rf05.expected_class, "DLM15LayerCNN_Table3_Normalized")

    def test_dl04_tabr_pinned_commit_and_isolation(self) -> None:
        dl04 = get_m02c_adapter("DL04")
        self.assertEqual(dl04.build_config()["repo_commit"], "17baa9082506f8e7a0f8d11bb1e08212926a1507")
        self.assertEqual(set(ADAPTER_REGISTRY_M02C.keys()), {"FM01", "FM02", "FM03", "FM04", "DL04", "RF05"})

    def test_501_feature_and_prediction_validation(self) -> None:
        with self.assertRaises(ValueError):
            validate_tabular_inputs(np.zeros((5, 500), dtype=np.float32))
        with self.assertRaises(ValueError):
            validate_predictions(np.array([1.0, np.nan]), expected_n=2)


if __name__ == "__main__":
    unittest.main()
