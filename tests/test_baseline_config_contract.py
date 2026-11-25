"""
tests/test_baseline_config_contract.py

Configuration contract tests for configs/baseline.yaml (M01.1 Section M).
"""

from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
BASELINE_YAML = ROOT / "configs" / "baseline.yaml"


class TestBaselineConfigContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with BASELINE_YAML.open("r", encoding="utf-8") as f:
            cls.cfg = yaml.safe_load(f)

    def test_seed_and_data_contract(self) -> None:
        self.assertEqual(self.cfg["seed"], 42)
        data = self.cfg["data"]
        self.assertEqual(data["path"], "data/raw/krkCMd_table.csv")
        self.assertEqual(data["target"], "MANwidth")
        self.assertEqual(data["feature_prefix"], "x")
        self.assertEqual(data["expected_feature_count"], 501)
        self.assertEqual(data["comparison_baselines"], ["DLMwidth", "AEDwidth"])

    def test_metadata_columns_are_strings_and_no_is_not_bool(self) -> None:
        meta = self.cfg["data"]["metadata_columns"]
        self.assertEqual(meta, ["No", "Profile", "Series", "Image", "Gridline", "Stage"])
        for col in meta:
            self.assertIsInstance(col, str, f"Metadata column {col!r} must be str, got {type(col).__name__}")
        self.assertNotIn(False, meta)

    def test_split_and_group_key_contract(self) -> None:
        split = self.cfg["split"]
        self.assertEqual(split["proposed_group_columns"], ["Series", "Image", "Gridline"])
        self.assertAlmostEqual(split["test_size"], 0.20)
        self.assertAlmostEqual(split["validation_size_of_remaining"], 0.20)

    def test_models_and_robustness_contract(self) -> None:
        self.assertIs(self.cfg["models"]["include_mlp"], False)
        rob = self.cfg["robustness"]
        self.assertEqual(rob["brightness_shifts"], [-20, 20])
        self.assertEqual(rob["contrast_scales"], [0.8, 1.2])
        self.assertEqual(rob["gaussian_noise_sigmas"], [5, 10])
        self.assertEqual(rob["smoothing_sigmas"], [1.0])


if __name__ == "__main__":
    unittest.main()
