"""
tests/test_m02a_adapters.py

Unit tests for M02A model adapters, input validation, 2D->3D signal adaptation,
feature order preservation, invalid output rejection, and registry integrity.
"""

import sys
import unittest
from pathlib import Path
import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.models.m02a_adapters import (  # noqa: E402
    ADAPTER_REGISTRY,
    adapt_2d_to_3d_signal,
    get_adapter,
    validate_predictions,
    validate_tabular_inputs,
)


class TestM02AAdaptersAndContracts(unittest.TestCase):
    def test_registry_has_32_unique_ids_and_5_m02a_targets(self) -> None:
        reg = yaml.safe_load((ROOT / "configs" / "model_registry.yaml").read_text(encoding="utf-8"))
        ids = [item["id"] for items in reg["categories"].values() for item in items]
        self.assertEqual(len(ids), 32)
        self.assertEqual(len(set(ids)), 32)
        self.assertEqual(set(ADAPTER_REGISTRY.keys()), {"ML04", "ML05", "ML06", "SG05", "SG06"})

    def test_rejects_wrong_feature_count(self) -> None:
        X_bad = np.zeros((10, 500), dtype=np.float32)
        with self.assertRaises(ValueError):
            validate_tabular_inputs(X_bad)

    def test_rejects_nan_or_inf_inputs(self) -> None:
        X_nan = np.zeros((5, 501), dtype=np.float32)
        X_nan[2, 10] = np.nan
        with self.assertRaises(ValueError):
            validate_tabular_inputs(X_nan)

    def test_rejects_invalid_prediction_shape_nan_inf(self) -> None:
        with self.assertRaises(ValueError):
            validate_predictions(np.zeros((20, 1)), expected_n=20)
        with self.assertRaises(ValueError):
            validate_predictions(np.array([1.0, np.nan]), expected_n=2)
        with self.assertRaises(ValueError):
            validate_predictions(np.array([1.0, np.inf]), expected_n=2)

    def test_2d_to_3d_signal_adaptation_preserves_order(self) -> None:
        X = np.arange(5 * 501, dtype=np.float32).reshape(5, 501)
        X_3d = adapt_2d_to_3d_signal(X)
        self.assertEqual(X_3d.shape, (5, 1, 501))
        np.testing.assert_array_equal(X_3d[:, 0, :], X)

    def test_unknown_model_id_raises(self) -> None:
        with self.assertRaises(KeyError):
            get_adapter("INVALID_ID")

    def test_sg06_identity_is_multirockethydra_not_multirocket(self) -> None:
        adapter = get_adapter("SG06")
        self.assertEqual(adapter.expected_class, "MultiRocketHydraRegressor")
        self.assertEqual(adapter.expected_module, "aeon.regression.convolution_based")


if __name__ == "__main__":
    unittest.main()
